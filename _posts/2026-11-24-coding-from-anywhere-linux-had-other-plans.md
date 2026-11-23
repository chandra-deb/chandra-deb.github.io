---
layout: post
title: "I Wanted to Code From Anywhere. My Linux Machines Had Other Plans."
description: "A remote AI coding lab turned into a very educational argument with Linux users, systemd, Syncthing, and SSH tunnels."
tags:
  - linux
  - networking
  - self-hosting
  - remote-development
  - devops
---

*24 November 2026 · Field notes from an unfinished but increasingly functional remote-development lab. No heroic uptime claims, no mysteriously perfect screenshots.*

I had what seemed like a perfectly reasonable idea: **what if I could keep coding on my projects from my phone, even when my home PC was switched off?**

I already had a Pop!_OS desktop, an Ubuntu cloud server, and AI coding agents. Surely I could connect the dots, put the heavy lifting on the server, and live happily ever after.

That was the plan.

Linux had a reading list prepared for me.

This is the story of how a simple remote-coding setup took me through SSH identities, Linux user isolation, persistent services, synchronization, and a pair of computers that knew each other existed but still refused to talk.

## The dream: code anywhere, don't leave my PC on

I wanted two ways to work:

- **At home:** use my Pop!_OS desktop and its local development environment.
- **Outside:** open T3 Code on my phone or tablet and let agents work on the Ubuntu server while my desktop is off.

I also wanted the source files to catch up automatically when I came home. Not another evening of manually copying project directories or remembering which machine had the latest version.

And I did **not** want to run a second copy of my entire backend stack on the server forever. That server was already hosting production services. I wanted to write code, not accidentally turn a development experiment into a surprise load test for real users.

Simple, right?

## Plot twist #1: “remote environment” and “remote host” are not quite the same thing

T3 Code already showed my local Pop!_OS environment and an Ubuntu environment connected over SSH. At first, it looked like everything was done.

Then I asked the question that matters: *what happens when I turn off the desktop?*

That exposed two separate concepts I'd been mixing together:

1. **Where an agent executes** — the local machine or the remote Ubuntu machine.
2. **Where the T3 Code service lives** — the process that manages access and sessions.

An SSH-connected environment launched from the desktop is useful, but it does not automatically guarantee a completely independent, always-on remote control plane. For my phone-with-PC-off goal, I needed a standalone T3 Code service on Ubuntu.

In hindsight, the mistake was assuming that **remote execution** automatically implied **independent remote access**.

They sound similar until you unplug the machine doing the controlling.

## Plot twist #2: the server was already somebody's house

The Ubuntu VM wasn't empty. It already had deployed applications under the existing server account.

Installing experimental coding tools into that account felt like inviting a construction crew into a restaurant during dinner service. Technically possible. Socially questionable.

So I created a separate Linux user for development:

```bash
# Run from the existing administrative account on Ubuntu
sudo adduser developer
```

That gives development its own home directory, SSH configuration, credentials, tools, and project files:

```text
/home/
├── existing-production-user/   # deployed applications
└── developer/                  # coding agents and experiments
```

I already had an SSH key and a working alias for the original account. Thankfully, I didn't need a brand-new key pair. I authorized the **existing public key** for `developer` and created a second SSH alias, `t3-dev`, for the new account.

The distinction is important: the public key goes into the new user's `authorized_keys`; the private key stays on my own computer.

Then I checked the new login:

```bash
ssh t3-dev
whoami
printf '%s\n' "$HOME"
```

```text
developer
/home/developer
```

A small victory. Separate credentials and separate files. Production's home directory stayed out of this experiment.

**Important caveat:** a separate Linux user is not a separate virtual machine. Both users still share CPU, RAM, disk, and the kernel. Also, giving the development user `sudo` or access to the production Docker daemon would weaken that isolation. I deliberately avoided that.

## The always-on part: systemd was the adult in the room

Next I installed T3 Code under the new `developer` account and configured its remote connection:

```bash
curl -fsSL https://t3.codes/install.sh | sh
~/.local/bin/t3 up
```

I used T3 Connect and verified the user service rather than trusting the reassuring feeling of seeing a command finish without an error.

```bash
systemctl --user is-active t3code.service
systemctl --user is-enabled t3code.service
loginctl show-user developer -p Linger
```

The actual results were:

```text
active
enabled
Linger=yes
```

That last line was surprisingly educational. `Linger=yes` allows the user's systemd manager to keep running after logout (and start without an active login), which is exactly what an always-on remote agent service needs.

For once, the computers were behaving.

## Then I checked the RAM, and the RAM checked me back

The server had about **1.9 GiB of physical RAM**, with roughly **598 MiB available** at the time I checked, and close to **1 GiB of swap in use**.

I had been thinking about cloning the whole backend development environment: API server, PostgreSQL, Redis, dependencies, containers, the works.

The memory numbers had other opinions.

So I made a deliberate decision:

- **T3 Code stays on all the time.** Its purpose is remote coding access.
- **The backend development stack stays off by default.** Most edits don't require a live database.
- **Occasional remote tests can be temporary later.** If I add them, they need resource limits and reliable cleanup.
- **Full integration testing can happen on my desktop** when I'm home.

No second permanent database, no accidental overlap with production, and no pretending that an extra Linux user magically creates extra RAM.

## Next problem: Git is version control, not a teleportation spell

I still needed the code to move between my local and remote machines. GitHub was already useful for commits and pull requests, but I wanted working-file synchronization too — including edits that hadn't been committed yet.

I chose **Syncthing** for the experiment. It can keep folders synchronized between devices and catch up when one device comes back online.

On each machine, Syncthing ran as a user service:

```bash
systemctl --user enable --now syncthing.service
```

The package itself was installed using the appropriate administrative account; the instance on Ubuntu ran under `developer`.

I opened the local dashboard on `127.0.0.1:8384` and accessed Ubuntu's dashboard through an SSH port forward. No public admin dashboard needed.

Then I paired the devices.

And this is where the comedy started.

## Two Linux machines. Two device IDs. Zero conversation.

On my Pop!_OS dashboard, Ubuntu appeared as a remote device.

On Ubuntu, there was no acceptance notification.

I waited. Refreshed. Looked at both tabs. Checked the IDs again.

Nothing.

Apparently, my computers had reached the *“I know who you are, but I'm not speaking to you”* stage of the relationship.

The first fix was straightforward: I added the Pop!_OS device ID **manually** on Ubuntu. Syncthing's device trust has to be configured on both sides; waiting for a popup isn't the only way.

Now both devices appeared, but the status was **Disconnected (Unused)**.

The “Unused” part gave us a clue: there wasn't yet a shared folder. So I created a disposable test folder, shared it from Pop!_OS, and accepted the folder on Ubuntu.

Surely that would do it.

Nope. Still disconnected. This time, connection attempts were timing out.

That's when the problem stopped being about pairing and started being about **network reachability**.

## The SSH tunnel that saved my remaining patience

SSH to Ubuntu was already working. But successful SSH access doesn't mean Syncthing's own TCP port, normally **22000**, is reachable over the network.

I could have started changing firewall rules on a server running production services. I preferred not to create a new public-facing port just to make two of my machines exchange files.

Instead, I reused the connection I already trusted: SSH.

On Pop!_OS, I ran:

```bash
ssh -N \
  -L 127.0.0.1:22001:127.0.0.1:22000 \
  t3-dev
```

Here's the mental model:

```text
Pop!_OS                           Ubuntu
Syncthing                          Syncthing
    |                                  ^
    v                                  |
127.0.0.1:22001 == encrypted SSH ==> 127.0.0.1:22000
```

The local port `22001` acts like a private doorway. Traffic entering there travels through SSH and emerges at Ubuntu's Syncthing listener on port `22000`.

Then, in **Pop!_OS Syncthing → Ubuntu device → Advanced → Addresses**, I replaced `dynamic` with:

```text
tcp://127.0.0.1:22001
```

And finally...

**It connected.**

Not a grand distributed-systems breakthrough. Just two computers successfully exchanging bytes through a tunnel after giving me an unsolicited networking lesson.

My reaction was approximately: *“yay..working”*.

Honestly, that felt earned.

## Why this worked (without the magic)

There were three separate layers to untangle:

1. **Identity:** each Syncthing device needs to recognize and trust the other device's ID.
2. **Folder sharing:** both devices need to agree which folder is shared and where it lives locally.
3. **Transport:** even with trust and a shared folder, packets still need an actual path between the devices.

We fixed the first two, but the third was still broken. SSH forwarding provided a working transport path without publicly exposing Syncthing's synchronization port.

That is why “SSH works” and “Syncthing works” weren't equivalent statements. Different services, different ports, different network paths.

## The things I got wrong

A useful lab notebook shouldn't quietly delete the embarrassing bits.

**I initially treated T3 Code's remote environment as if it automatically solved independent phone access.** It didn't answer the question of where the control service runs.

**I briefly considered duplicating a complete backend environment on a small production VM.** Checking available memory changed that plan before it became a problem.

**I waited for a Syncthing approval notification as if the UI were the entire protocol.** Adding the second device ID manually was enough to establish reciprocal trust.

**I treated pairing and folder sharing as though they proved network connectivity.** They don't. The timeouts mattered more than the “Unused” label once a folder was shared.

The recurring lesson: when something fails, identify *which layer is failing* before changing everything in sight.

## Where the lab stands today

The verified pieces are:

- T3 Code is installed under a dedicated Ubuntu development user, with the service **active**, **enabled**, and lingering configured.
- Syncthing is installed on both computers.
- The two Syncthing instances successfully connected **through a manually started SSH tunnel**.

The next steps are still work in progress: make the tunnel start and reconnect automatically on Pop!_OS, verify synchronization after a full desktop shutdown/restart cycle, and only then enable carefully scoped synchronization for real project directories.

I also need to be disciplined about Git. If I exclude `.git` internals from file syncing, the source files may match while branch state and commit histories differ. And two AI agents editing the same synchronized files simultaneously is an excellent way to manufacture merge conflicts with extra steps.

For actual projects, I plan to keep Git as the authority for history and use file sync cautiously, with explicit exclusions for secrets, dependencies, databases, and generated files.

## A note to my future self

I started this project because I wanted to code from anywhere without leaving my PC turned on.

I ended up learning more than I expected about what it means for a service to be *independent*, how Linux isolates users, why a background process survives logout, and why recognizing another machine isn't the same as reaching it over a network.

Also, I didn't capture this journey properly on video. Naturally, the idea to document the funny failures arrived *after* most of them had happened. Excellent timing, as usual.

Next time, I'm recording the terminal, the errors, and probably my face when Linux says “permission denied” for the seventh time.

For now, I have the commands, the decisions, the mistakes, and one working SSH tunnel.

And my future self has one less excuse to leave the desktop running all night.

*To be continued — preferably with fewer disconnected devices.*