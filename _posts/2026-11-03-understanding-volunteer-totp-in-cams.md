---
layout: post
title: "Understanding Volunteer TOTP in CAMS (Without Sacrificing Your Sanity)"
description: "A beginner-friendly tour of CAMS volunteer QR validation: HMAC tokens, time buckets, API flow, and the database checks behind attendance."
tags:
  - backend
  - security
  - attendance
  - fastapi
  - qr
---

Security tutorials often begin with a sentence like "It is just a little cryptography." That sentence has caused many perfectly good afternoons to disappear.

CAMS volunteer attendance is easier to understand once we separate the jobs involved:

- the volunteer app displays a short-lived QR token;
- the student's app sends the scanned data to the API;
- the backend recomputes the token and decides whether the attendance is allowed.

The phone can be fast. The server must be skeptical.

## The problem this solves

In volunteer mode, a student scans a QR code displayed by an assigned volunteer. This is useful at a doorway, a competition checkpoint, a food distribution table, or anywhere an organizer needs to know not only that a student attended, but also which volunteer verified them.

A static QR code would be easy to screenshot and reuse. A rotating QR code makes that screenshot expire quickly.

The CAMS implementation uses a **TOTP-style** design. It is TOTP-style rather than a drop-in implementation of the RFC 6238 format: CAMS builds its own context-bound payload and signs it with HMAC-SHA256.

That distinction matters. The name is less important than the contract:

```text
same secret + same volunteer + same window + same time bucket = same token
```

Change any one of those values and the token changes.

## The four ingredients

The live implementation in `app/utils/volunteer_token.py` uses four ingredients:

1. A secret key generated for the volunteer's shift.
2. A five-second time bucket.
3. A payload containing the volunteer's student ID, the attendance window ID, and the bucket.
4. An HMAC-SHA256 digest, shortened to 16 hexadecimal characters for the QR payload.

The interval is calculated like this:

$$
interval = \\left\\lfloor \\frac{unix\\_time}{5} \\right\\rfloor
$$

In Python:

```python
ROTATION_INTERVAL_SECONDS = 5


def get_current_interval() -> int:
    return int(time.time()) // ROTATION_INTERVAL_SECONDS
```

If the Unix timestamp is `1712550007`, the interval is:

$$
\\left\\lfloor 1712550007 / 5 \\right\\rfloor = 342510001
$$

The token does not change every time the app redraws the screen. It changes when time crosses a five-second boundary. The QR should still be refreshed on that schedule so the display does not become a museum exhibit for an already-aging token.

## What the token actually signs

CAMS creates a small, deliberately boring payload:

```python
payload = f"{volunteer_id}:{window_id}:{interval}"
token = hmac.new(
    secret_key.encode("utf-8"),
    payload.encode("utf-8"),
    hashlib.sha256,
).hexdigest()[:16]
```

Suppose the values are:

```text
volunteer_id = 456
window_id    = 123
interval     = 342510001
```

The signed message is:

```text
456:123:342510001
```

This context binding is important. A token generated for volunteer `456` and window `123` should not be portable to another volunteer or another attendance window. The token is not merely "a code that is valid right now"; it is a code for a particular person, place in the workflow, and moment in time.

## A shift gets a fresh secret

When a volunteer starts a shift, the backend generates a new 64-character hexadecimal secret with `secrets.token_hex(32)`. It stores that secret on the volunteer assignment and returns it in `StartShiftResponse`, along with the server's Unix time and the active volunteer windows.

The response contains both `assignment_id` and `student_id`. This is a small naming trap with a large ability to waste debugging time:

- `assignment_id` identifies the `SessionVolunteer` database row;
- `student_id` identifies the person and is the ID used in the QR payload and HMAC input.

The QR must use `student_id`, not the assignment row ID.

The server time is useful for clock calibration. If a volunteer phone is 12 seconds slow, its local interval calculation may disagree with the backend. A client can estimate the offset at shift start and use an adjusted clock for token generation. CAMS also exposes time-sync information so the app can give a human-readable warning instead of making the volunteer negotiate with an invisible clock demon.

A secret is powerful, so it should be treated as shift-scoped sensitive material: keep it in protected app state, do not log it, and do not put it in analytics events.

## The grace period is not what the old draft said

Validation begins with the server's current interval:

```python
current_interval = get_current_interval()

for offset in range(GRACE_INTERVALS + 1):
    interval = current_interval - offset
    expected_token = generate_token_for_interval(
        secret_key,
        volunteer_id,
        window_id,
        interval,
    )

    if hmac.compare_digest(
        provided_token.lower(), expected_token.lower()
    ):
        return interval

return None
```

The current constant is:

```python
GRACE_INTERVALS = 2
```

That means the backend accepts:

1. the current interval;
2. one previous interval;
3. two previous intervals.

With five-second intervals, the oldest accepted token can be nearly 15 seconds old, depending on where the request lands relative to an interval boundary. So the useful mental model for the current code is **roughly 15 seconds of acceptance**, not 10 seconds.

This is one of those moments where the source code wins an argument with a comment. Some older CAMS documentation still describes a one-interval grace period. When documenting security behavior, check the constant and the validation loop together.

The comparison uses `hmac.compare_digest`, which avoids the ordinary early-exit comparison behavior that can leak timing information. It does not magically solve every security problem, but it is the right comparison primitive for this job.

The grace period is backward-only. CAMS does not accept a token from a future interval. That is a sensible boundary: tolerate a slightly slow device or network request, but do not let a client invent tomorrow's QR code.

## The request flow, end to end

Here is the real flow in human-sized pieces.

### 1. A president assigns volunteers

An assigned student becomes a volunteer for an activity session. The volunteer is still a student; the assignment grants a session-specific operational role.

### 2. The volunteer starts the shift

The volunteer app calls the start-shift endpoint. The backend verifies the assignment is active, generates a fresh secret, records the shift start time, and returns the secret plus active volunteer windows.

The QR generator can now work locally:

```text
interval = floor(adjusted_unix_time / 5)
payload  = student_id:window_id:interval
token    = HMAC-SHA256(secret_key, payload)[:16]
```

No request is needed just to rotate the QR every five seconds. That reduces API traffic and lets the display keep changing during a brief connectivity hiccup.

### 3. A student scans the QR

The scanned data is sent to the attendance endpoint. A volunteer-mode request looks like this:

```json
{
  "type": "volunteer",
  "window_id": 123,
  "volunteer_id": 456,
  "token": "a1b2c3d4e5f6a7b8"
}
```

The field named `volunteer_id` is, slightly confusingly, the volunteer's **student ID**, not `SessionVolunteer.id`. The schema documents this because future-you deserves at least one fewer mystery.

### 4. The backend validates the token and the business rules

`AttendanceService.mark_attendance_volunteer` does not stop at "the HMAC matched." It checks the workflow around the token too:

1. The attendance window exists.
2. The student has not already marked attendance for that window.
3. The volunteer belongs to the window's session and is active.
4. The volunteer has started a shift and has a secret.
5. The HMAC matches the current or accepted previous interval.
6. The window really uses volunteer mode.
7. The student is registered for the activity.
8. The window is active and the current UTC time is between `opens_at` and `closes_at`.
9. The attendance record and volunteer audit log are written together.

This layered validation is the important lesson. A valid cryptographic token is evidence that the QR data was produced by someone with the shift secret. It is not, by itself, permission to attend an activity.

## The database remembers the human story

The token is temporary, but the attendance record is durable.

`attendance_checks` stores the student's attendance and has a unique composite index on `(window_id, student_id)`. That database constraint prevents duplicate attendance for the same student and window, even if two requests arrive at almost the same time.

For volunteer verification, the record also stores:

```python
verified_by_student_id = volunteer_id
verification_mode = VerificationMode.VOLUNTEER_VERIFIED
```

Then `volunteer_scan_logs` records the audit relationship:

```text
which volunteer -> verified which student -> at which window -> when
```

The service also catches a possible race condition around the duplicate check. Two requests might both observe "no existing attendance" before either inserts. The unique database constraint remains the final authority; an `IntegrityError` is converted into the same friendly conflict response.

That is a good general backend pattern: application checks improve the normal path, but database constraints defend the invariant.

## What this design does well

### It limits replay

A screenshot may contain a genuine token, but the token ages out quickly. The short interval narrows the useful replay window.

### It binds data to context

A token is tied to a volunteer and an attendance window, not just to the current time.

### It keeps QR rotation cheap

The volunteer app can generate tokens locally. The API only handles the meaningful event: a student actually submitting attendance.

### It leaves an audit trail

Attendance is associated with the verifying volunteer, and the scan log supports later statistics and review.

### It handles ordinary clock drift

The backward grace intervals and server-time calibration help when two phones do not agree perfectly about the current second.

## What it does not magically solve

This design is not a force field. Someone with access to the live secret on a compromised device could generate valid tokens. The short token lifetime reduces exposure; it does not replace device security, authentication, rate limiting, monitoring, or organizer review.

Also, the secret is returned to the volunteer client because the client generates the QR. That is a deliberate trade-off: less polling and better offline behavior in exchange for protecting the secret on the device. Security decisions are often less like choosing a perfect lock and more like choosing which doors need alarms.

Finally, `GRACE_INTERVALS` changes the replay window. It should be treated as a security and usability setting, tested at interval boundaries, and kept consistent across backend, frontend, and documentation.

## The short version

CAMS volunteer attendance uses a per-shift secret and a five-second time bucket to generate context-bound HMAC tokens. The volunteer app rotates the QR locally. The student scans it and submits the token with the window ID and volunteer's student ID. The backend recomputes the expected token for the current and two previous intervals, then applies the actual attendance rules: assignment, shift, mode, registration, time window, and duplicate protection. Finally, it records both attendance and who verified it.

Or, in one sentence:

> The frontend makes the QR quickly, but the backend decides whether the story is believable.

That is the useful pattern to carry into other systems: short-lived, context-bound, server-verified tokens paired with database-backed business constraints.
