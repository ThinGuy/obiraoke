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

1. **obiraoke/lib/youtube_dl.py -- upgrade_youtubedl()**
   yt-dlp self-upgrade (`-U` flag and pip fallback) is skipped when `$SNAP` is
   set. A warning is logged directing the user to `snap refresh`. The function
   returns the current version immediately.

2. **obiraoke/routes/admin.py -- /shutdown and /reboot routes**
   Both the route handler and `delayed_halt()` check for `$SNAP`. The route
   returns a 503 JSON response (`{"error": "... unavailable in snap confinement"}`). The `delayed_halt` fallback also logs a warning and returns
   early, preventing `os.system("shutdown now")` and `os.system("reboot")` from
   being called.

3. **obiraoke/routes/admin.py -- /expand_fs route (raspi-config)**
   Same 503 pattern as shutdown/reboot. `raspi-config --expand-rootfs` is
   blocked under snap confinement at both the route level and inside
   `delayed_halt()`.

4. **obiraoke/lib/omxclient.py -- OMXClient.play_file()**
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

## libcaca exclusion

libcaca is an ffmpeg transitive dependency providing ASCII art rendering that
obiraoke does not use. Its OpenGL plugin (`libgl_plugin.so`) pulls in libGLU
and libglut, which are not staged in the snap, causing missing-dependency lint
warnings from `snapcraft pack`. Only the OpenGL plugin under
`usr/lib/x86_64-linux-gnu/caca/libgl_plugin*` is excluded from prime -- not the
entire libcaca library. `libcaca.so.0` must remain because ffmpeg links against
it directly; removing it causes four new missing-dependency warnings.

## Dependency resolution strategy

Missing-dependency warnings from `snapcraft pack` mean a staged binary links
against a library that is not present in the snap. The correct fix is to add the
missing library as a stage-package so it ships inside the snap. Never fix a
missing-dependency warning by excluding the consumer from prime -- that just
moves the breakage from a lint warning to a runtime crash.

Prime exclusions are only valid for genuinely unused libraries that have no
consumers inside the snap. If any staged binary links against a library, that
library must be present.

### libslang2 and libtheora0

`libslang2` is required because libcaca and libavdevice link against it.
`libtheora0` is required because libavcodec, libavformat, libavfilter, and
libavdevice all link against it. Both were previously (incorrectly) excluded
from prime, which caused cascading missing-dependency warnings. They are now
added as explicit stage-packages so they are always present.

## Unused library exclusions

Libraries excluded from prime because nothing in the snap links against them:

- `caca/libgl_plugin` -- libcaca OpenGL plugin, pulls in unstaged libGLU/libglut
- `libGLX_mesa` -- Mesa GLX provider, not needed without a display server
- `libXxf86vm` -- X11 video mode extension, unused in headless snap
- `libcaca++` -- C++ bindings for libcaca, unused by ffmpeg
- `libcjson_utils` -- cJSON utility extensions unused by ffmpeg at runtime
- `libfftw3_omp`, `libfftw3_threads` -- OpenMP/threaded FFTW variants unused by ffmpeg
- `libflite_cmu_grapheme_lang`, `libflite_cmu_grapheme_lex`, `libflite_cmu_indic_lang`, `libflite_cmu_indic_lex`, `libflite_cmu_time_awb` -- Flite TTS language/lexicon data unused by obiraoke
- `libhwy_contrib`, `libhwy_test` -- Highway SIMD test/contrib libraries
- `libicui18n` -- ICU internationalization library, no staged binary links against it
- `libicuio`, `libicutest`, `libicutu` -- ICU I/O, test, and tool utility libraries not needed at runtime
- `libjacknet`, `libjackserver` -- JACK audio server components (obiraoke uses PulseAudio)
- `libpulse-simple` -- simplified PulseAudio API, unused (obiraoke uses libpulse0 directly)
- `libsphinxad` -- PocketSphinx audio device library unused by obiraoke
- `libtheora.so` -- top-level Theora convenience lib (`libtheora.so.0`); ffmpeg links against `libtheoradec`/`libtheoraenc`, not `libtheora.so` itself
- `libxcb-glx` -- XCB GLX extension, unused in headless snap
- `libzvbi-chains` -- VBI capture chain library unused by obiraoke

## Strict Confinement Path Normalization (Sprint 5)

Switched snap confinement from `devmode` to `strict` in `snap/snapcraft.yaml`.
All application paths are now gated behind `os.environ.get("SNAP")` so the app
resolves confined paths when running as a snap and keeps existing behavior
otherwise. Grade remains `devel`.

### Path changes in `obiraoke/lib/get_platform.py`

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

- **`obiraoke/lib/file_resolver.py`** -- Already uses `tempfile.gettempdir()`
  for all temporary file operations. No hardcoded `/tmp` paths.
- **Test files** -- Mock values like `/tmp/12345` in test fixtures are arbitrary
  strings passed to mocked functions and do not affect runtime behavior.

### Layout section

No `layout` section was added to `snapcraft.yaml`. All paths are either within
snap-writable areas (`$SNAP_USER_DATA`, private `/tmp`) or covered by existing
interface plugs (`home` for `$HOME/obiraoke-songs`, `audio-playback` for the
PulseAudio socket).

## librubberband2 for pitch shifting

librubberband2 required for ffmpeg pitch shift support. Added as a
stage-package so ffmpeg's rubberband audio filter is functional inside
the snap. The corresponding build-package (`librubberband-dev`) is also
added so ffmpeg can compile against rubberband headers.

## Renamed --dolphly to --mascot-mode

The `--dolphly` CLI flag was renamed to `--mascot-mode` to give the option a
self-documenting name. The flag, help text, and internal variable
(`args.mascot_mode`) were updated in `obiraoke/lib/args.py`. The underlying
assets (`dolphly.png`, `the_drive_by_visualdon.mp4`) are unchanged.

## ffmpeg built from upstream source tarball with rubberband support

The stock Ubuntu ffmpeg package in core24 is not compiled with
`--enable-librubberband`, so staging `librubberband2` alone does not enable
pitch shifting. The ffmpeg part uses the autotools plugin with
`source: https://ffmpeg.org/releases/ffmpeg-7.1.tar.gz` to build ffmpeg from
the upstream source tarball with `--prefix=/usr`, `--enable-librubberband`,
`--enable-gpl`, `--enable-nonfree`, `--disable-static`, `--enable-shared`, and
documentation generation disabled. The previous `source: apt:ffmpeg` form failed
because `apt:` is not a valid snapcraft source type -- snapcraft only recognises
URLs, local paths, and VCS repositories as source values. Building from the
upstream tarball also avoids depending on Ubuntu's source packaging layout.

## libasound.so.2 must NOT be excluded from prime

`libasound.so.2` must remain in the snap. The ALSA plugin modules in
`libasound2-plugins` (e.g. `libasound_module_pcm_pulse.so`) load it at runtime
via `dlopen`. Because no staged binary links against it directly, dependency
linters report it as unused -- but excluding it causes silent audio failure
when ALSA plugins attempt to call back into the core ALSA library.

`libslang.so.2` is a genuine convenience symlink with no runtime consumers and
remains excluded.

## Help text rebranding (args.py)

Two help strings in `obiraoke/lib/args.py` still referenced the upstream
project name. `--limit-user-songs-by` mentioned "Pikaraoke" (now "Obiraoke")
and `--hide-overlay` mentioned "pikaraoke QR code" (now "obiraoke QR code").

## Wrapper entry point rename (Sprint 6)

The snap wrapper script (`snap/local/wrapper`) invoked `$SNAP/bin/pikaraoke` but
the entry point was renamed to `obiraoke` in `pyproject.toml` during Sprint 6.
The exec line now calls `$SNAP/bin/obiraoke`. The wrapper entry point must match
the pyproject.toml entry point name exactly.

## ffmpeg runtime dependencies

The custom-built ffmpeg binary links against libass, libfdk-aac, and libunibreak
at runtime. The snapcraft linter flagged these as missing dependencies. Added
`libass9`, `libfdk-aac2`, and `libunibreak5` as stage-packages on the obiraoke
part so they ship inside the snap.

## Shared songs directory ($SNAP_COMMON)

The snap songs directory was changed from `$HOME/obiraoke-songs` to
`$SNAP_COMMON/obiraoke-songs` so that songs are shared across all users on the
system. `$SNAP_COMMON` (`/var/snap/obiraoke/common`) is writable by the snap
daemon and persists across refreshes. This avoids each user maintaining a
separate song library.

## Snap configuration interface

The snap supports runtime configuration via `snap set obiraoke key=value`.
The wrapper script (`snap/local/wrapper`) reads each key with `snapctl get`
and passes it as a CLI argument to obiraoke. The configure hook
(`snap/hooks/configure`) validates values when they are set.

Supported keys:

- **port** -- TCP listen port. Must be numeric, 1-65535. Passed as `--port`.
- **admin-password** -- Admin interface password. Passed as `--admin-password`.
- **download-path** -- Song download directory. Defaults to
  `$SNAP_COMMON/obiraoke-songs` if not set. Passed as `--download-path`.
- **log-level** -- Logging level (DEBUG, INFO, WARNING, ERROR). Passed as
  `--log-level`.
- **headless** -- Boolean. If `true`, adds `--headless` flag. Defaults to
  headless when not set.
- **streaming-format** -- Must be `hls` or `mp4`. Passed as
  `--streaming-format`.

Example usage:

```
sudo snap set obiraoke port=8080
sudo snap set obiraoke streaming-format=mp4
sudo snap set obiraoke headless=true
```

## Install hook creates $SNAP_COMMON subdirectories

`$SNAP_COMMON` (`/var/snap/obiraoke/common`) is owned by root. When obiraoke
runs as a normal user, it cannot create subdirectories there. Attempting to
download songs to `$SNAP_COMMON/obiraoke-songs` fails with "Permission denied"
if the directory does not already exist.

The fix is `snap/hooks/install`, which runs as root during `snap install`. It
creates `$SNAP_COMMON/obiraoke-songs` with mode 0777 so any user can write to
it. The configure hook (`snap/hooks/configure`) also creates the directory if
missing, covering the case where the install hook did not run or the directory
was removed.

Any future `$SNAP_COMMON` subdirectory that non-root users need must follow the
same pattern: create it in the install hook with world-writable permissions.

## Autostart and daemon mode

The snap includes a second app entry, `obiraoke-server`, configured as a
`daemon: simple` service with `restart-condition: on-failure`. It uses the same
wrapper script and plugs as the interactive `obiraoke` app but runs under
systemd.

**Autostart configuration key.** `snap set obiraoke autostart=true` enables
the daemon via `snapctl start --enable`; setting it to `false` disables and
stops it via `snapctl stop --disable`. The configure hook validates the value
and rejects anything other than `true` or `false`.

**File logging.** When the wrapper detects daemon mode (`SNAP_INSTANCE_NAME`
and `JOURNAL_STREAM` both set), it redirects stdout and stderr to
`$SNAP_COMMON/obiraoke.log`. Before starting, it checks the log file size and
rotates it (moving to `.log.1`) if it exceeds 10 MB. The install hook creates
`$SNAP_COMMON/logs` (0755) and seeds `$SNAP_COMMON/obiraoke.log` (0644).

## Daemon install-mode: disable

The `obiraoke-server` daemon in `snap/snapcraft.yaml` previously started
automatically on `snap install`. This is wrong for a karaoke app -- the user
should explicitly opt in with `snap set obiraoke autostart=true`. Added
`install-mode: disable` to the `obiraoke-server` app stanza so the daemon is
installed but not started or enabled until the user sets `autostart=true`,
which the configure hook handles via `snapctl start --enable`.

## Port pre-flight check (app.py)

The gevent `WSGIServer` raises an `OSError` traceback when the listen port is
already in use. Added a socket-based pre-flight check in `main()` before
`server.start()`. If the port is occupied, a clear error message is logged
("Port NNNN is already in use. Is obiraoke already running?") and the process
exits cleanly with `sys.exit(1)` instead of dumping a traceback.

## Package rename (pikaraoke -> obiraoke)

The Python package directory was renamed from `pikaraoke/` to `obiraoke/`. All
internal imports (`from pikaraoke...` / `import pikaraoke`) were updated to
`from obiraoke...` / `import obiraoke`. The following non-Python files were
also updated to reference the new package path:

- `pyproject.toml` -- entry point, hatch packages list, coverage omit paths
- `release-please-config.json` -- changelog-path and version-file
- `build_scripts/docker/Dockerfile` -- COPY directive for the package directory
- `.github/workflows/ci.yml` -- pytest `--cov=` target
- `.github/workflows/api-docs.yml` -- inline Python import

Files NOT renamed: Docker user/home paths, upstream install scripts, snap
wrapper environment variables, user-visible product name strings, and static
asset paths inside the package.

## bulma.min.css replaced with obiraoke.css

`bulma.min.css` was replaced with `obiraoke/static/obiraoke.css`, a custom
stylesheet built on the UI spec color system (Section 2) with the Ubuntu
variable font stack. All Bulma class names used in templates are re-implemented
with spec-compliant values. No border-radius on structural elements.

`bulma-dark.css` remains as a temporary safety net during the transition. It
will be removed once the replacement is fully validated across all pages.

The `!important` override blocks in `custom.css` that existed to beat the Bulma
cascade have been removed since they are no longer needed.
