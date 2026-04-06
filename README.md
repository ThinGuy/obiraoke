# Ubuntu Coreaoke

![OB-01](coreaoke/static/images/logo.png)

## Meet OB-01

OB-01 is the mascot of Ubuntu Coreaoke — an orange robot with a big smile
and an even bigger song library. He's a close friend to Canonical's Field
Engineers, who know him well from the OrangeBox: a self-contained rack of
Intel NUCs and network gear powered by Ubuntu and MAAS, built to show the
world what open source can do in a box you can carry on a plane.

## The Art of Possible

Most people look at a karaoke app and see a karaoke app. I looked at
[vicwomg's PiKaraoke](https://github.com/vicwomg/pikaraoke) — one of the
best open source karaoke engines ever written — and saw something else: a
fully-featured media platform waiting to be repackaged, confined, and shipped
as a first-class Ubuntu application.

No rewrite required. No new engine. Just the art of possible: take excellent
open source software, wrap it properly, expose the right interfaces, and
suddenly a Raspberry Pi on a shelf becomes a venue-grade karaoke station with
digital signage, remote administration, and snap-managed updates.

That's the power of Ubuntu Core and Snaps.

## What It Does

Ubuntu Coreaoke is a strictly-confined snap built on PiKaraoke. Any device
running Ubuntu Core or snapd instantly becomes a full-featured karaoke station:

- 📱 **Instant Mobile Remote** — search and queue from any phone, no app required
- 📺 **Full-screen Player** — background video, animated splash, OB-01 on stage
- 🌐 **YouTube & Local Media** — stream from the web or play your own files
- 🎹 **Live Pitch Shifting** — every song in every key
- 🎯 **QR Code Access** — scan and sing, no typing required
- 🔒 **Admin Protection** — password-lock queue and settings
- 📡 **Digital Signage** — dedicated queue and lobby displays for venues
- 🐧 **Snap-managed** — updates, config, and autostart via `snap set`

## Snaps and Ubuntu Core

This project is a love letter to the snap ecosystem. A snap is a
self-contained, sandboxed application package that runs identically on every
Linux distribution that supports snapd — from a $35 Raspberry Pi to an
enterprise server rack.

Ubuntu Core takes this further: an operating system built entirely from snaps,
designed for embedded and IoT devices. It boots immutably, updates atomically,
and enforces strict confinement on every application. There is no package
manager, no drift, no configuration rot. The device does exactly one thing and
does it reliably.

Ubuntu Coreaoke is a strictly-confined Core-grade snap. It declares every
interface it needs — audio, network, display — and the system grants only
those. It ships its own Python runtime, FFmpeg build, and all dependencies
inside the snap boundary. Nothing leaks out. Nothing from the host leaks in.

One command installs it. One command updates it. One command removes it
without a trace.

This is what modern Linux application delivery looks like.

## Supported Platforms

Ubuntu Coreaoke runs on any platform with snapd installed. If you don't have
snapd yet, [install it here](https://snapcraft.io/docs/tutorials/install-the-daemon/).

Check [here](https://snapcraft.io/docs/tutorials/install-the-daemon/) for any
distributions added since this guide was last updated.

- [![Arch Linux](https://res.cloudinary.com/canonical/image/fetch/f_svg,q_auto,fl_sanitize,w_48/https%3A%2F%2Fassets.ubuntu.com%2Fv1%2Ffeca0fc0-Distro_Logo_ArchLinux.svg)](https://snapcraft.io/install/snapd/arch) [Arch Linux](https://snapcraft.io/install/snapd/arch)
- [![CentOS](https://res.cloudinary.com/canonical/image/fetch/f_svg,q_auto,fl_sanitize,w_48/https%3A%2F%2Fassets.ubuntu.com%2Fv1%2Facf876d9-Distro_Logo_CentOS.svg)](https://snapcraft.io/install/snapd/centos) [CentOS](https://snapcraft.io/install/snapd/centos)
- [![Debian](https://res.cloudinary.com/canonical/image/fetch/f_svg,q_auto,fl_sanitize,w_48/https%3A%2F%2Fassets.ubuntu.com%2Fv1%2Fcfdc1144-Distro_Logo_Debian.svg)](https://snapcraft.io/install/snapd/debian) [Debian](https://snapcraft.io/install/snapd/debian)
- [![elementary OS](https://res.cloudinary.com/canonical/image/fetch/f_svg,q_auto,fl_sanitize,w_48/https%3A%2F%2Fassets.ubuntu.com%2Fv1%2Fc0c09661-Distro_Logo_Elementary.svg)](https://snapcraft.io/install/snapd/elementary) [elementary OS](https://snapcraft.io/install/snapd/elementary)
- [![Fedora](https://res.cloudinary.com/canonical/image/fetch/f_auto,q_auto,fl_sanitize,w_48/https%3A%2F%2Fassets.ubuntu.com%2Fv1%2Fc93d842f-fedora.png)](https://snapcraft.io/install/snapd/fedora) [Fedora](https://snapcraft.io/install/snapd/fedora)
- [![KDE Neon](https://res.cloudinary.com/canonical/image/fetch/f_svg,q_auto,fl_sanitize,w_48/https%3A%2F%2Fassets.ubuntu.com%2Fv1%2Fd0593902-Distro_Logo_KDE%2BNeon.svg)](https://snapcraft.io/install/snapd/kde-neon) [KDE Neon](https://snapcraft.io/install/snapd/kde-neon)
- [![Kubuntu](https://res.cloudinary.com/canonical/image/fetch/f_svg,q_auto,fl_sanitize,w_48/https%3A%2F%2Fassets.ubuntu.com%2Fv1%2F7ab50a06-Distro_Logo_Kubuntu.svg)](https://snapcraft.io/install/snapd/kubuntu) [Kubuntu](https://snapcraft.io/install/snapd/kubuntu)
- [![Manjaro](https://res.cloudinary.com/canonical/image/fetch/f_svg,q_auto,fl_sanitize,w_48/https%3A%2F%2Fassets.ubuntu.com%2Fv1%2F4635a0bd-Distro_Logo_Manjaro.svg)](https://snapcraft.io/install/snapd/manjaro) [Manjaro](https://snapcraft.io/install/snapd/manjaro)
- [![Pop!_OS](https://res.cloudinary.com/canonical/image/fetch/f_svg,q_auto,fl_sanitize,w_48/https%3A%2F%2Fassets.ubuntu.com%2Fv1%2Fc7ca0dfa-Distro_Logo_Pop.svg)](https://snapcraft.io/install/snapd/pop) [Pop!\_OS](https://snapcraft.io/install/snapd/pop)
- [![openSUSE](https://res.cloudinary.com/canonical/image/fetch/f_svg,q_auto,fl_sanitize,w_48/https%3A%2F%2Fassets.ubuntu.com%2Fv1%2F610301c6-Distro_Logo_OpenSUSE.svg)](https://snapcraft.io/install/snapd/opensuse) [openSUSE](https://snapcraft.io/install/snapd/opensuse)
- [![Red Hat Enterprise Linux](https://res.cloudinary.com/canonical/image/fetch/f_svg,q_auto,fl_sanitize,w_48/https%3A%2F%2Fassets.ubuntu.com%2Fv1%2Fbe89e41a-red-hat-2019-primary-stacked.svg)](https://snapcraft.io/install/snapd/rhel) [Red Hat Enterprise Linux](https://snapcraft.io/install/snapd/rhel)
- [![Ubuntu](https://res.cloudinary.com/canonical/image/fetch/f_svg,q_auto,fl_sanitize,w_48/https%3A%2F%2Fassets.ubuntu.com%2Fv1%2F8e43097f-cof_square_512x512.svg)](https://snapcraft.io/install/snapd/ubuntu) [Ubuntu](https://snapcraft.io/install/snapd/ubuntu)
- [![Raspberry Pi](https://res.cloudinary.com/canonical/image/fetch/f_svg,q_auto,fl_sanitize,w_48/https%3A%2F%2Fassets.ubuntu.com%2Fv1%2F193cb6ac-logo-raspberry-pi.svg)](https://snapcraft.io/install/snapd/raspian) [Raspberry Pi](https://snapcraft.io/install/snapd/raspian)

## Installing / Upgrading / Removing

```sh
# Install
sudo snap install coreaoke

# Upgrade
sudo snap refresh coreaoke

# Remove (preserves song library)
sudo snap remove coreaoke

# Remove and purge all downloaded content
sudo snap remove coreaoke --purge
```

## Digital Signage

Connect additional screens to dedicated display channels:

| URL | Purpose |
|-----|---------|
| `/splash` | Main karaoke player |
| `/splash?channel=queue` | Scrolling queue for lobby or waiting area |
| `/splash?channel=lobby` | Venue entrance — next singer, QR code, song count |

Any browser on any device on the same network can drive a signage screen.
No client software required.

## Configuration

Ubuntu Coreaoke is configured entirely via `snap set` — no config files to
edit, no environment variables to export.

| Key | Description | Example |
|-----|-------------|---------|
| `port` | HTTP listen port (default: 5555) | `sudo snap set coreaoke port=8080` |
| `admin-password` | Lock down admin features | `sudo snap set coreaoke admin-password=secret` |
| `download-path` | Custom songs directory | `sudo snap set coreaoke download-path=/mnt/songs` |
| `log-level` | Logging verbosity | `sudo snap set coreaoke log-level=DEBUG` |
| `headless` | Run without local browser | `sudo snap set coreaoke headless=true` |
| `streaming-format` | `hls` or `mp4` | `sudo snap set coreaoke streaming-format=mp4` |
| `autostart` | Start on boot | `sudo snap set coreaoke autostart=true` |
| `proxy` | HTTP proxy for yt-dlp | `sudo snap set coreaoke proxy=http://proxy.example.com:3128` |

## Credits

Ubuntu Coreaoke stands on the work of others.

[vicwomg](https://github.com/vicwomg) built
[PiKaraoke](https://github.com/vicwomg/pikaraoke) — the engine that makes
all of this possible. Every core karaoke feature is his work.

Built with: yt-dlp · FFmpeg · Flask · Socket.IO · HLS.js · Selectize.js ·
Fontello · Ubuntu Variable Font

Snap packaging, UI redesign, branding, and Ubuntu Core integration by
[ThinGuy](https://github.com/ThinGuy).

Ubuntu Core and snapd by [Canonical](https://canonical.com).
