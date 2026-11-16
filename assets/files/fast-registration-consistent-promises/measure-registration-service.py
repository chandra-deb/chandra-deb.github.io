"""Small service timing sample, never an HTTP/load/durability benchmark.

Run from the backend root with .venv/bin/python. Owns disposable local Redis
and PostgreSQL containers; never uses application URLs or existing databases.
Redis persistence is disabled and PostgreSQL data is on the fixture's tmpfs.
"""
import asyncio
from collections import Counter
import json
import math
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
import uuid
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
# Establish inert application settings before importing application modules.
from tests import conftest as _isolated_settings  # noqa: F401
from tests.database import temporary_postgres
from tests import factories
from app import models  # noqa: F401
from app.services.activity_service import ActivityService
from app.services.registration_service import RegistrationService
from redis.asyncio import Redis
from redis.exceptions import ConnectionError as RedisConnectionError
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlmodel import SQLModel, select, func
from sqlmodel.ext.asyncio.session import AsyncSession
from app.models.activity_registration import ActivityRegistration
from app.models.registration_waitlist import RegistrationWaitlist


def docker(*args):
    return subprocess.run(["docker", *args], check=True, capture_output=True,
                          text=True, timeout=180).stdout.strip()


def summary(values):
    ordered = sorted(values)
    return {f"p{p}_ms": round(ordered[math.ceil(p / 100 * len(ordered)) - 1], 3)
            for p in (50, 95, 99)} | {"samples": len(values)}


async def measure(url, port):
    engine = create_async_engine(url, pool_size=2, max_overflow=0)
    maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    client = Redis(host="127.0.0.1", port=port, decode_responses=True)
    try:
        for attempt in range(50):
            try:
                await client.ping()
                break
            except RedisConnectionError:
                if attempt == 49:
                    raise
                await asyncio.sleep(0.1)
        async with engine.begin() as connection:
            await connection.run_sync(SQLModel.metadata.create_all)
        runs, admissions, commits = [], [], []
        async with maker() as session:
            pg_version = str((await session.exec(select(func.version()))).one())
            for run in range(3):
                # Setup hashes are irrelevant to registration and outside timing.
                with patch.object(factories, "hash_password", return_value="measurement-only"):
                    activity = await factories.create_activity(
                        session, max_participants=120, waitlist_max=220)
                    students = [await factories.create_student(session) for _ in range(220)]
                await session.commit()
                await ActivityService.warm_activity_cache(session, client, activity.id)
                await session.commit()  # no setup transaction/lock remains open
                run_admission, run_commit, outcomes = [], [], Counter()
                for index, student in enumerate(students):
                    start = time.perf_counter_ns()
                    receipt = await RegistrationService.register_atomic(
                        client, activity.id, student.id, session=session)
                    admitted = time.perf_counter_ns()
                    payload = json.loads(await client.hget(
                        f"activity:{activity.id}:participants", str(student.id)))
                    start_commit = time.perf_counter_ns()
                    assert await RegistrationService.save_atomic_registration(session, payload)
                    committed = time.perf_counter_ns()
                    if index >= 20:
                        run_admission.append((admitted - start) / 1e6)
                        run_commit.append((committed - start_commit) / 1e6)
                        outcomes[receipt.status] += 1
                # Actual commits: no test outer transaction/savepoint wrapper.
                registered = (await session.exec(select(func.count()).select_from(
                    ActivityRegistration).where(ActivityRegistration.activity_id == activity.id))).one()
                waiting = (await session.exec(select(func.count()).select_from(
                    RegistrationWaitlist).where(RegistrationWaitlist.activity_id == activity.id))).one()
                assert (registered, waiting) == (120, 100)
                assert outcomes == {"REGISTERED": 100, "WAITLIST": 100}
                await session.commit()
                admissions.extend(run_admission)
                commits.extend(run_commit)
                runs.append({"run": run + 1, "admission": summary(run_admission),
                             "postgres_commit_call": summary(run_commit),
                             "measured_outcomes": dict(outcomes),
                             "final_rows_including_warmup": {"registered": registered, "waiting": waiting}})
        info = await client.info("server")
        return {"redis_version": info["redis_version"], "postgres_version": pg_version,
                "admission": summary(admissions), "postgres_commit_call": summary(commits),
                "runs": runs}
    finally:
        await client.aclose()
        await engine.dispose()


def main():
    name = "cams-blog-timing-" + uuid.uuid4().hex[:12]
    started = False
    try:
        docker("run", "--detach", "--rm", "--name", name,
               "--publish", "127.0.0.1::6379", "redis:alpine",
               "redis-server", "--save", "", "--appendonly", "no")
        started = True
        port = int(docker("port", name, "6379/tcp").rsplit(":", 1)[1])
        # Force the fixture to create local containers; ignore any admin URL.
        with patch.dict(os.environ):
            os.environ.pop("TEST_POSTGRES_ADMIN_URL", None)
            with temporary_postgres() as url:
                result = asyncio.run(measure(url, port))
        result.update({
            "date_local": "2026-11-16", "timezone": "Asia/Shanghai",
            "python": platform.python_version(), "platform": platform.platform(),
            "logical_cpus_visible": os.cpu_count(),
            "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
            "docker_server_version": docker("version", "--format", "{{.Server.Version}}"),
            "method": {"runs": 3, "warmup_per_run": 20, "measured_per_run": 200,
                       "concurrent_clients": 1, "activities_per_run": 1,
                       "percentiles": "nearest-rank, pooled samples",
                       "redis_persistence": "disabled", "postgres_data": "tmpfs",
                       "transport": "Python service calls to Docker loopback ports",
                       "excluded": ["HTTP, TLS, authentication, browser", "worker scheduling, stream consumption, XACK",
                                    "receipt HGET between stages", "setup and warmup"],
                       "note": "Not a throughput, contention, HTTP, or disk-durability benchmark"}})
        target = Path("docs/reviews/evidence/registration-service-timing-2026-11-16.json")
        target.write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result, indent=2))
    finally:
        if started:
            docker("rm", "--force", name)


if __name__ == "__main__":
    main()
