# Changelog

All notable changes to Ubuntu Coreaoke are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).
Versions follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] — 2026-04-08

First public release of Ubuntu Coreaoke.

Built on [vicwomg/pikaraoke](https://github.com/vicwomg/pikaraoke) —
all core karaoke functionality is vicwomg's work.

### Added

**Snap packaging**
- Strictly-confined snap targeting Ubuntu Core and any snapd-enabled Linux
- Full Python 3.12 runtime, FFmpeg, yt-dlp, and deno bundled inside the snap
- PulseAudio wiring for snap strict confinement
- `snap set` configuration for all runtime options
- Install and configure hooks with validation
- Preseed support: pre-load song library from a URL tarball on first run
- Removable media interface for USB song libraries
- Grade: devel pending store review

**White-label branding**
- `app-name` snap key — display name shown everywhere in the UI
- `app-icon` snap key — custom sidebar/topbar icon
- `theme` snap key — switch logo, background video, and music in one command
- Theme directory structure under `$SNAP_COMMON/themes/<name>/`
- Branding context injected into all templates automatically

**Digital signage**
- `?channel=queue` — scrolling queue display for lobby screens
- `?channel=lobby` — venue entrance display with next singer, QR code, song count
- Directory-based custom channels under `$SNAP_COMMON/signage/`
- `channel.yaml` configuration per channel: layout, timing, assets
- Background video cycling, QR code rotation, background sound support
- `/signage/qr?url=` endpoint for runtime QR generation
- `/signage/assets/<channel>/<subdir>/<file>` for asset serving

**UI redesign**
- Full Canonical Vanilla Framework implementation
- Dark sidebar (`#262626`) with Ubuntu Orange (`#e95420`) accent
- Responsive sidebar width (`min-width:200px; width:25vw; max-width:300px`)
- Collapsible Goodies menu (About, Docs, SBOM) with localStorage persistence
- Tweaks nav item for settings (in-sidebar, non-disruptive)
- Username display at top of nav, clickable to rename, defaults to "Singer"
- Active nav item toggle — click again to collapse sidebar content
- Full Vanilla Framework button colors: green for positive, red for destructive
- Fontello icon set throughout
- Ubuntu variable font from assets.ubuntu.com

**Operator features**
- `/docs` — full operator guide for venue owners (plain English, no jargon)
- `/sbom` — Software Bill of Materials with JSON export
- `/info` (Tweaks) — all settings configurable from the sidebar
- Lockdown mode: `snap set coreaoke lockdown=true` hides Goodies, blocks routes
- Logo position control: 7 positions for splash screen logo placement
- System info: platform, OS version, snapd version, Ubuntu Pro status

**Player stability**
- Persistent splash master via 5-second grace period on disconnect
- Song survives sidebar navigation — only master can end a song
- Background video `currentTime` persists across Search page reloads
- Background video fallback chain: theme → built-in → none

**Credits & About**
- `/credits` (About) — project acknowledgements, GitHub link, system info
- Credits overlay fires on player panel when About is visited
- Tagline: "Built with ♥ using Ubuntu and Snapcraft"

### Changed

- Renamed throughout from pikaraoke → coreaoke
- `--mascot-mode` CLI argument removed (use themes instead)
- Added CLI arguments: `--logo-position`, `--app-name`, `--app-icon`,
  `--theme`, `--lockdown`
- Browse sort label changed to "By Filename | By Date"
- Info page renamed to "Settings" in nav; accessible as Tweaks
- Default username changed to "Singer"

### Fixed

- Strict confinement path normalization throughout
- yt-dlp self-upgrade disabled in snap confinement (handled by `snap refresh`)
- Shutdown/reboot/raspi-config routes return 503 under confinement
- OMXPlayer calls skipped under confinement
- libpulse0, libasound2 staged for audio under strict confinement
- libcaca OpenGL plugin excluded from prime to prevent lint warnings
- core24 PYTHONPATH set to `$SNAP/lib/python3.12/site-packages`

---

## Upstream

Ubuntu Coreaoke is built on [PiKaraoke](https://github.com/vicwomg/pikaraoke)
by [vicwomg](https://github.com/vicwomg). For upstream changes prior to this
fork, see the [PiKaraoke changelog](https://github.com/vicwomg/pikaraoke/blob/master/CHANGELOG.md).
