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
