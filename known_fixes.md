# Known Fixes

## Wrapper script (Sprint 1)

The app command must be `bin/wrapper`, not `bin/pikaraoke`. The snap uses a
wrapper part (dump plugin, source `snap/local`) that stages the wrapper script
into `bin/wrapper`. Direct invocation of the Python entry point fails inside
confinement because environment setup is needed first.

## PYTHONPATH (Sprint 1)

`PYTHONPATH` must be set to `$SNAP/lib/python3.12/site-packages` in the app
environment. Without it the Python interpreter inside the snap cannot find the
installed packages and the application fails to import its own modules.

## Bundled deno runtime

yt-dlp requires a JavaScript runtime to extract download URLs from some sites.
Without one, certain YouTube videos fail during metadata extraction. Deno is
bundled in the snap as `bin/deno` so yt-dlp can invoke it inside the
confinement boundary without relying on the host system.

## Staged libpulse0

The `audio-playback` snap interface provides access to the host PulseAudio
socket, but the PulseAudio client library (`libpulse0`) must still be present
inside the snap for applications to connect. Without it, audio output silently
fails even though the interface is connected.

## Snap Runtime Guards

The following locations are gated behind `os.environ.get("SNAP")` to ensure
graceful degradation under snap strict confinement.

1. **pikaraoke/lib/youtube_dl.py -- upgrade_youtubedl()**
   yt-dlp self-upgrade (`-U` flag and pip fallback) is skipped when `$SNAP` is
   set. A warning is logged directing the user to `snap refresh`. The function
   returns the current version immediately.

2. **pikaraoke/routes/admin.py -- /shutdown and /reboot routes**
   Both the route handler and `delayed_halt()` check for `$SNAP`. The route
   returns a 503 JSON response (`{"error": "... unavailable in snap confinement"}`). The `delayed_halt` fallback also logs a warning and returns
   early, preventing `os.system("shutdown now")` and `os.system("reboot")` from
   being called.

3. **pikaraoke/routes/admin.py -- /expand_fs route (raspi-config)**
   Same 503 pattern as shutdown/reboot. `raspi-config --expand-rootfs` is
   blocked under snap confinement at both the route level and inside
   `delayed_halt()`.

4. **pikaraoke/lib/omxclient.py -- OMXClient.play_file()**
   The hardcoded `/usr/bin/omxplayer` path is unreachable under snap strict
   confinement. When `$SNAP` is set, `play_file()` logs a warning and returns
   immediately. omxplayer is legacy; all playback is handled by the browser.

## Audio Interface (Sprint 4)

Snap strict confinement isolates the application from host audio devices. Three
pieces are required for audio to work:

1. **libpulse0 (stage-package)** -- The PulseAudio client library. The
   `audio-playback` plug grants access to the host PulseAudio socket, but
   without the client library inside the snap, nothing can connect to it.
   FFmpeg and any other process that probes audio devices at init time need
   this library present.

2. **libasound2 and libasound2-plugins (stage-packages)** -- The ALSA user-space
   library and its plugin set. Some FFmpeg builds enumerate ALSA devices before
   falling back to PulseAudio. Without libasound2 the probe segfaults or
   returns an opaque error. The plugins package includes the PulseAudio ALSA
   plugin (`libasound_module_pcm_pulse.so`), which routes ALSA output through
   PulseAudio transparently.

3. **PULSE_SERVER and PULSE_RUNTIME_PATH wiring** -- Inside confinement the
   PulseAudio socket is at `/run/user/<uid>/pulse/native`. The snap environment
   sets `PULSE_SERVER=unix:/run/user/1000/pulse/native` and
   `PULSE_RUNTIME_PATH=/run/user/1000/pulse` so the client library finds the
   socket without probing. A helper script (`snap/local/pulseaudio-setup`)
   is sourced by the wrapper at launch to set these variables dynamically
   using `id -u`, with a static fallback in `snapcraft.yaml` for UID 1000.

4. **libpulse-dev (build-package)** -- Required at build time so that FFmpeg
   and Python audio bindings can compile against PulseAudio headers. Without it,
   optional PulseAudio support may be silently omitted during compilation.

## core24 uses platforms not architectures

The `architectures` key is not supported in core24-based snaps. Snapcraft
rejects it at build time. The equivalent for core24 is the `platforms` key:

```yaml
platforms:
  amd64:
```

This was changed in `snap/snapcraft.yaml` from the old form:

```yaml
architectures:
  - build-on: [amd64]
```

## Strict Confinement Path Normalization (Sprint 5)

Switched snap confinement from `devmode` to `strict` in `snap/snapcraft.yaml`.
All application paths are now gated behind `os.environ.get("SNAP")` so the app
resolves confined paths when running as a snap and keeps existing behavior
otherwise. Grade remains `devel`.

### Path changes in `pikaraoke/lib/get_platform.py`

1. **Config directory (`get_data_directory()`)**

   - Non-snap: `~/.pikaraoke` (unchanged)
   - Snap: `$SNAP_USER_DATA/.pikaraoke`
   - Why: Under strict confinement the home plug does not grant access to
     dotfiles. `$SNAP_USER_DATA` (`~/snap/obiraoke/current`) is always writable
     by the confined process without any extra plugs.

2. **Songs directory (`get_default_dl_dir()`)**

   - Non-snap: `~/pikaraoke-songs` (unchanged, with legacy fallbacks)
   - Snap: `$HOME/obiraoke-songs`
   - Why: The `home` plug grants access to non-hidden files in `$HOME`. Using
     the rebranded `obiraoke-songs` name avoids confusion with the upstream
     project name. Legacy directory checks are skipped under snap because
     previous snap installs never created them.

3. **Temp directory (`file_resolver.py`)**

   - Already uses `tempfile.gettempdir()` exclusively. The snap runtime provides
     a private `/tmp` automatically, so no code changes were needed.

4. **Windows paths (`%APPDATA%/pikaraoke`, `~\pikaraoke-songs`)**

   - No changes. Snaps do not run on Windows.

### Files not changed

- **`pikaraoke/lib/file_resolver.py`** -- Already uses `tempfile.gettempdir()`
  for all temporary file operations. No hardcoded `/tmp` paths.
- **Test files** -- Mock values like `/tmp/12345` in test fixtures are arbitrary
  strings passed to mocked functions and do not affect runtime behavior.

### Layout section

No `layout` section was added to `snapcraft.yaml`. All paths are either within
snap-writable areas (`$SNAP_USER_DATA`, private `/tmp`) or covered by existing
interface plugs (`home` for `$HOME/obiraoke-songs`, `audio-playback` for the
PulseAudio socket).
