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

1. **coreaoke/lib/youtube_dl.py -- upgrade_youtubedl()**
   yt-dlp self-upgrade (`-U` flag and pip fallback) is skipped when `$SNAP` is
   set. A warning is logged directing the user to `snap refresh`. The function
   returns the current version immediately.

2. **coreaoke/routes/admin.py -- /shutdown and /reboot routes**
   Both the route handler and `delayed_halt()` check for `$SNAP`. The route
   returns a 503 JSON response (`{"error": "... unavailable in snap confinement"}`). The `delayed_halt` fallback also logs a warning and returns
   early, preventing `os.system("shutdown now")` and `os.system("reboot")` from
   being called.

3. **coreaoke/routes/admin.py -- /expand_fs route (raspi-config)**
   Same 503 pattern as shutdown/reboot. `raspi-config --expand-rootfs` is
   blocked under snap confinement at both the route level and inside
   `delayed_halt()`.

4. **coreaoke/lib/omxclient.py -- OMXClient.play_file()**
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
coreaoke does not use. Its OpenGL plugin (`libgl_plugin.so`) pulls in libGLU
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
- `libflite_cmu_grapheme_lang`, `libflite_cmu_grapheme_lex`, `libflite_cmu_indic_lang`, `libflite_cmu_indic_lex`, `libflite_cmu_time_awb` -- Flite TTS language/lexicon data unused by coreaoke
- `libhwy_contrib`, `libhwy_test` -- Highway SIMD test/contrib libraries
- `libicui18n` -- ICU internationalization library, no staged binary links against it
- `libicuio`, `libicutest`, `libicutu` -- ICU I/O, test, and tool utility libraries not needed at runtime
- `libjacknet`, `libjackserver` -- JACK audio server components (coreaoke uses PulseAudio)
- `libpulse-simple` -- simplified PulseAudio API, unused (coreaoke uses libpulse0 directly)
- `libsphinxad` -- PocketSphinx audio device library unused by coreaoke
- `libtheora.so` -- top-level Theora convenience lib (`libtheora.so.0`); ffmpeg links against `libtheoradec`/`libtheoraenc`, not `libtheora.so` itself
- `libxcb-glx` -- XCB GLX extension, unused in headless snap
- `libzvbi-chains` -- VBI capture chain library unused by coreaoke

## Strict Confinement Path Normalization (Sprint 5)

Switched snap confinement from `devmode` to `strict` in `snap/snapcraft.yaml`.
All application paths are now gated behind `os.environ.get("SNAP")` so the app
resolves confined paths when running as a snap and keeps existing behavior
otherwise. Grade remains `devel`.

### Path changes in `coreaoke/lib/get_platform.py`

1. **Config directory (`get_data_directory()`)**

   - Non-snap: `~/.pikaraoke` (unchanged)
   - Snap: `$SNAP_USER_DATA/.pikaraoke`
   - Why: Under strict confinement the home plug does not grant access to
     dotfiles. `$SNAP_USER_DATA` (`~/snap/coreaoke/current`) is always writable
     by the confined process without any extra plugs.

2. **Songs directory (`get_default_dl_dir()`)**

   - Non-snap: `~/pikaraoke-songs` (unchanged, with legacy fallbacks)
   - Snap: `$HOME/coreaoke-songs`
   - Why: The `home` plug grants access to non-hidden files in `$HOME`. Using
     the rebranded `coreaoke-songs` name avoids confusion with the upstream
     project name. Legacy directory checks are skipped under snap because
     previous snap installs never created them.

3. **Temp directory (`file_resolver.py`)**

   - Already uses `tempfile.gettempdir()` exclusively. The snap runtime provides
     a private `/tmp` automatically, so no code changes were needed.

4. **Windows paths (`%APPDATA%/pikaraoke`, `~\pikaraoke-songs`)**

   - No changes. Snaps do not run on Windows.

### Files not changed

- **`coreaoke/lib/file_resolver.py`** -- Already uses `tempfile.gettempdir()`
  for all temporary file operations. No hardcoded `/tmp` paths.
- **Test files** -- Mock values like `/tmp/12345` in test fixtures are arbitrary
  strings passed to mocked functions and do not affect runtime behavior.

### Layout section

No `layout` section was added to `snapcraft.yaml`. All paths are either within
snap-writable areas (`$SNAP_USER_DATA`, private `/tmp`) or covered by existing
interface plugs (`home` for `$HOME/coreaoke-songs`, `audio-playback` for the
PulseAudio socket).

## librubberband2 for pitch shifting

librubberband2 required for ffmpeg pitch shift support. Added as a
stage-package so ffmpeg's rubberband audio filter is functional inside
the snap. The corresponding build-package (`librubberband-dev`) is also
added so ffmpeg can compile against rubberband headers.

## Renamed --dolphly to --mascot-mode

The `--dolphly` CLI flag was renamed to `--mascot-mode` to give the option a
self-documenting name. The flag, help text, and internal variable
(`args.mascot_mode`) were updated in `coreaoke/lib/args.py`. The underlying
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

Two help strings in `coreaoke/lib/args.py` still referenced the upstream
project name. `--limit-user-songs-by` mentioned "Pikaraoke" (now "Coreaoke")
and `--hide-overlay` mentioned "pikaraoke QR code" (now "coreaoke QR code").

## Wrapper entry point rename (Sprint 6)

The snap wrapper script (`snap/local/wrapper`) invoked `$SNAP/bin/pikaraoke` but
the entry point was renamed to `coreaoke` in `pyproject.toml` during Sprint 6.
The exec line now calls `$SNAP/bin/coreaoke`. The wrapper entry point must match
the pyproject.toml entry point name exactly.

## ffmpeg runtime dependencies

The custom-built ffmpeg binary links against libass, libfdk-aac, and libunibreak
at runtime. The snapcraft linter flagged these as missing dependencies. Added
`libass9`, `libfdk-aac2`, and `libunibreak5` as stage-packages on the coreaoke
part so they ship inside the snap.

## Shared songs directory ($SNAP_COMMON)

The snap songs directory was changed from `$HOME/coreaoke-songs` to
`$SNAP_COMMON/coreaoke-songs` so that songs are shared across all users on the
system. `$SNAP_COMMON` (`/var/snap/coreaoke/common`) is writable by the snap
daemon and persists across refreshes. This avoids each user maintaining a
separate song library.

## Snap configuration interface

The snap supports runtime configuration via `snap set coreaoke key=value`.
The wrapper script (`snap/local/wrapper`) reads each key with `snapctl get`
and passes it as a CLI argument to coreaoke. The configure hook
(`snap/hooks/configure`) validates values when they are set.

Supported keys:

- **port** -- TCP listen port. Must be numeric, 1-65535. Passed as `--port`.
- **admin-password** -- Admin interface password. Passed as `--admin-password`.
- **download-path** -- Song download directory. Defaults to
  `$SNAP_COMMON/coreaoke-songs` if not set. Passed as `--download-path`.
- **log-level** -- Logging level (DEBUG, INFO, WARNING, ERROR). Passed as
  `--log-level`.
- **headless** -- Boolean. If `true`, adds `--headless` flag. Defaults to
  headless when not set.
- **streaming-format** -- Must be `hls` or `mp4`. Passed as
  `--streaming-format`.

Example usage:

```
sudo snap set coreaoke port=8080
sudo snap set coreaoke streaming-format=mp4
sudo snap set coreaoke headless=true
```

## Install hook creates $SNAP_COMMON subdirectories

`$SNAP_COMMON` (`/var/snap/coreaoke/common`) is owned by root. When coreaoke
runs as a normal user, it cannot create subdirectories there. Attempting to
download songs to `$SNAP_COMMON/coreaoke-songs` fails with "Permission denied"
if the directory does not already exist.

The fix is `snap/hooks/install`, which runs as root during `snap install`. It
creates `$SNAP_COMMON/coreaoke-songs` with mode 0777 so any user can write to
it. The configure hook (`snap/hooks/configure`) also creates the directory if
missing, covering the case where the install hook did not run or the directory
was removed.

Any future `$SNAP_COMMON` subdirectory that non-root users need must follow the
same pattern: create it in the install hook with world-writable permissions.

## Autostart and daemon mode

The snap includes a second app entry, `coreaoke-server`, configured as a
`daemon: simple` service with `restart-condition: on-failure`. It uses the same
wrapper script and plugs as the interactive `coreaoke` app but runs under
systemd.

**Autostart configuration key.** `snap set coreaoke autostart=true` enables
the daemon via `snapctl start --enable`; setting it to `false` disables and
stops it via `snapctl stop --disable`. The configure hook validates the value
and rejects anything other than `true` or `false`.

**File logging.** When the wrapper detects daemon mode (`SNAP_INSTANCE_NAME`
and `JOURNAL_STREAM` both set), it redirects stdout and stderr to
`$SNAP_COMMON/coreaoke.log`. Before starting, it checks the log file size and
rotates it (moving to `.log.1`) if it exceeds 10 MB. The install hook creates
`$SNAP_COMMON/logs` (0755) and seeds `$SNAP_COMMON/coreaoke.log` (0644).

## Daemon install-mode: disable

The `coreaoke-server` daemon in `snap/snapcraft.yaml` previously started
automatically on `snap install`. This is wrong for a karaoke app -- the user
should explicitly opt in with `snap set coreaoke autostart=true`. Added
`install-mode: disable` to the `coreaoke-server` app stanza so the daemon is
installed but not started or enabled until the user sets `autostart=true`,
which the configure hook handles via `snapctl start --enable`.

## Port pre-flight check (app.py)

The gevent `WSGIServer` raises an `OSError` traceback when the listen port is
already in use. Added a socket-based pre-flight check in `main()` before
`server.start()`. If the port is occupied, a clear error message is logged
("Port NNNN is already in use. Is coreaoke already running?") and the process
exits cleanly with `sys.exit(1)` instead of dumping a traceback.

## Package rename (pikaraoke -> coreaoke)

The Python package directory was renamed from `pikaraoke/` to `coreaoke/`. All
internal imports (`from pikaraoke...` / `import pikaraoke`) were updated to
`from coreaoke...` / `import coreaoke`. The following non-Python files were
also updated to reference the new package path:

- `pyproject.toml` -- entry point, hatch packages list, coverage omit paths
- `release-please-config.json` -- changelog-path and version-file
- `build_scripts/docker/Dockerfile` -- COPY directive for the package directory
- `.github/workflows/ci.yml` -- pytest `--cov=` target
- `.github/workflows/api-docs.yml` -- inline Python import

Files NOT renamed: Docker user/home paths, upstream install scripts, snap
wrapper environment variables, user-visible product name strings, and static
asset paths inside the package.

## bulma.min.css replaced with coreaoke.css

`bulma.min.css` was replaced with `coreaoke/static/coreaoke.css`, a custom
stylesheet built on the UI spec color system (Section 2) with the Ubuntu
variable font stack. All Bulma class names used in templates are re-implemented
with spec-compliant values. No border-radius on structural elements.

`bulma-dark.css` remains as a temporary safety net during the transition. It
will be removed once the replacement is fully validated across all pages.

The `!important` override blocks in `custom.css` that existed to beat the Bulma
cascade have been removed since they are no longer needed.

## Link and navbar color specificity (coreaoke.css)

Added `!important` to the base `a` and `a:hover` color rules in
`coreaoke/static/coreaoke.css` so they win over `bulma-dark.css` in the
cascade. Also added `!important` to `.navbar-item`, `.navbar-item:hover`, and
`.navbar-item.is-active` color rules, and `background-color: transparent !important` on `.navbar-item:hover` to prevent bulma-dark from painting a
visible hover background on navbar links.

## Removed build_scripts/ and docs/ directories

Deleted `build_scripts/` (Docker build helpers, CI smoke tests, install scripts)
and `docs/` (GitHub Pages config and legacy README). These are upstream
artifacts that do not apply to the coreaoke snap packaging. `.github/` is
retained.

## Snap proxy configuration key

Added a `proxy` snap configuration key that passes an HTTP proxy URL to yt-dlp
via `--youtubedl-proxy`. The wrapper script (`snap/local/wrapper`) reads the
key with `snapctl get proxy` and appends the argument when set. The configure
hook comment block and `snapcraft.yaml` description keys section are updated
to document the new key.

Usage: `snap set coreaoke proxy=http://proxy.example.com:3128`

## fontello.css load order and spec-link class

Links throughout the app rendered as browser-default blue instead of `#69c`
because `fontello/css/fontello.css` loaded after `coreaoke.css` in
`base.html`, resetting link colors in the cascade.

**Fix:**

1. Moved the `fontello.css` `<link>` in `coreaoke/templates/base.html` to load
   **before** `coreaoke.css` so the custom `a` color rules win.

2. Added `.spec-link` and `.spec-link:hover` rules in `coreaoke.css`
   (`color: #69c !important` / `color: #70bbc2 !important`) as a targeted
   class for links that must always use the dark-background link color.

3. Applied `class="spec-link"` to the "Sort by Date", "Sort by Alphabetical",
   and "Edit all songs" links in `coreaoke/templates/files.html`.

The base `a` and `a:hover` rules already had `!important` and were correctly
at the top level with no parent selector -- no changes needed there.

## White link colors for dark background

The base `a` color in `coreaoke.css` was `#69c` (a blue inherited from the
Vanilla Framework dark-background link token). On a `#262626` dark background,
blue links look out of place and are harder to read than white text.

**Changes:**

1. **`coreaoke/static/coreaoke.css`** -- Changed `a { color: #69c }` to
   `color: #ffffff` and `a:hover` from `#70bbc2` to `#e95420` (Ubuntu Orange).
   Updated `.spec-link` and `.spec-link:hover` to match.

2. **`coreaoke/templates/files.html`** -- Added `#alpha-bar a` rule with
   `color: rgba(255,255,255,0.7)` for a subtly dimmed default state,
   `#alpha-bar a:hover` with `color: #ffffff`, and kept the existing
   `#alpha-bar a.alpha-active` rule at `color: #e95420` with `font-weight: 700`.

## pyproject.toml readme field pointed to missing file

The `readme` field in `pyproject.toml` referenced `docs/README.md`, which was
removed when the `docs/` directory was deleted. Updated the field to point to
`README.md` in the repo root and created a minimal `README.md` with the project
heading.

## Italic replaced with Ubuntu Thin (weight 100)

All italic usage in `coreaoke/static/coreaoke.css` was replaced with Ubuntu Thin
(font-weight 100, font-style normal). This gives emphasized text a visually
distinct lighter weight instead of a slanted style, which fits better with the
Ubuntu variable font design.

**Changes in `coreaoke.css`:**

1. Added `em, i { font-style: normal; font-weight: 100; }` to the reset/base
   section so all native italic elements render as thin weight instead.

2. Changed `.is-italic` from `font-style: italic` to
   `font-style: normal; font-weight: 100`.

3. The `@font-face` for "Ubuntu variable" italic in `base.html` is kept but no
   longer used for italic styling -- thin weight handles that role.

**Affected elements in `search.html`:**

- Two `<p class="is-italic">` help-text paragraphs (lines 616, 620) now render
  at weight 100 instead of italic.
- `<i>` tags wrapping search terms in the "Searching YouTube for" loader and
  "Search results for" label pick up the `em, i` reset rule automatically.

## Browse page (files.html) link color fixes

Audited `coreaoke/templates/files.html` (the `/browse` route) for elements
rendering blue instead of spec-compliant colors. Four issues found and fixed:

1. **`#alpha-bar` had `border-radius: 4px`** -- Removed. No border-radius on
   structural elements per UI spec.

2. **Active alpha-bar letter had no selected state** -- Added `alpha-active`
   class via Jinja conditional (`{% if letter == l %}`) that applies
   `color: #e95420 !important` and `font-weight: 700` to the currently
   selected letter. The "show all" icon and "#" numeric link also highlight
   when active.

3. **`.add-song-link.has-text-success` rendered as `#69c` (blue)** -- The
   global `a { color: #69c !important }` rule in `coreaoke.css` overrode the
   `.has-text-success` class, making the green "add to queue" icons appear
   blue. Added a higher-specificity rule
   `a.add-song-link.has-text-success { color: #0e8420 !important }` in the
   template `<style>` block to restore the correct green color.

4. **`.pagination-link.is-current` used `#69c` background** -- The active
   pagination page got its background from `bulma-dark.css`
   (`var(--dark-link)` = `#69c`). Active/selected elements must use `#e95420`
   per spec. Added an override rule in the template `<style>` block:
   `.pagination-link.is-current { background-color: #e95420 !important; border-color: #e95420 !important }`.

## Snap config directory moved from dotfile to visible path

Under snap strict confinement the `home` plug does not grant access to hidden
directories (those starting with `.`). The config directory was
`$SNAP_USER_DATA/.pikaraoke`, which is a hidden directory inside the user's snap
data area. Changed to `$SNAP_USER_DATA/config` in two places:

1. **`coreaoke/lib/get_platform.py` -- `get_data_directory()`** -- The snap
   branch now joins `base_path` with `"config"` instead of `".pikaraoke"`.

2. **`snap/local/wrapper`** -- The `PIKARAOKE_CONFIG_DIR` export now points to
   `$SNAP_USER_DATA/config` instead of `$SNAP_USER_DATA/.pikaraoke`.

Only the directory path changed. The database filename and all other file names
inside the directory are unchanged.

## Thin font weight bumped from 100 to 200

The `em, i` reset rule and `.is-italic` class in `coreaoke/static/coreaoke.css`
used `font-weight: 100`, which rendered nearly invisible at small sizes on some
displays. Changed both rules to `font-weight: 200` (extra-light) for better
legibility while preserving the lighter-than-body visual distinction.

## Rename pikaraoke.db and remaining pikaraoke internal names to coreaoke

Renamed the SQLite database filename from `pikaraoke.db` to `coreaoke.db` in
`coreaoke/lib/karaoke_database.py`. Also renamed all remaining internal
references to "pikaraoke" in Python code to "coreaoke":

- **Database**: `pikaraoke.db` to `coreaoke.db` in `karaoke_database.py`
- **Data directories**: `~/.pikaraoke` to `~/.coreaoke` (Linux/macOS),
  `%APPDATA%/pikaraoke` to `%APPDATA%/coreaoke` (Windows) in `get_platform.py`
- **Download directories**: default paths changed from `pikaraoke-songs` to
  `coreaoke-songs` in `get_platform.py`; legacy path checks kept as-is for
  migration from upstream pikaraoke installs
- **Default download path**: `/usr/lib/pikaraoke/songs` to
  `/usr/lib/coreaoke/songs` in `karaoke.py`
- **System user**: `"Pikaraoke"` to `"Coreaoke"` in `queue_manager.py` and
  `download_manager.py`
- **Function name**: `parse_pikaraoke_args` to `parse_coreaoke_args` in
  `args.py` and `app.py`
- **Template variable**: `pikaraoke_version` to `coreaoke_version` in
  `routes/info.py` and `templates/info.html`
- **User-facing strings**: updated exit message and log messages in
  `routes/admin.py`, `routes/now_playing.py`, `karaoke.py`, and
  `lib/args.py`
- **Tests**: updated all corresponding test assertions

## Removed legacy files and Raspberry Pi code

Removed files and directories not needed for a snap-only Linux project:

- **uv.lock** -- UV package manager lockfile, not used by snapcraft. Added to
  `.gitignore` to prevent re-commit.
- **release-please-config.json** -- Google release-please automation config,
  not relevant for snap releases.
- **code_quality/** -- Pre-commit config directory, removed entirely.
- **coreaoke/static/bulma.min.css** -- Bulma CSS framework, replaced by
  coreaoke.css. Dead weight.
- **coreaoke/static/bulma-dark.css** -- Unlinked from base.html, dead weight.
  Removed the `<link>` tag from `base.html` as well.

Removed all Raspberry Pi specific code and references:

- **coreaoke/lib/raspi_wifi_config.py** -- Deleted entirely. RaspiWiFi AP mode
  configuration utility, not applicable to snap.
- **coreaoke/lib/omxclient.py** -- Deleted entirely. omxplayer is RPi legacy;
  all playback is browser-based.
- **coreaoke/lib/get_platform.py** -- Removed `is_raspberry_pi()` function and
  all code paths that called it (RPi branch in `get_platform()`, RPi default
  download path fallback in `get_default_dl_dir()`).
- **coreaoke/karaoke.py** -- Removed `is_raspberry_pi` attribute and the RPi
  IP-retry loop in `get_url()`.
- **coreaoke/routes/admin.py** -- Removed `/expand_fs` route entirely and the
  raspi-config branch from `delayed_halt()`.
- **coreaoke/lib/current_app.py** -- Removed raspi-config branch from
  `delayed_halt()`.
- **coreaoke/lib/browser.py** -- Removed RPi-specific browser profile skip and
  `--disable-dev-shm-usage` flag.
- **coreaoke/routes/splash.py** -- Removed RaspiWiFi import and AP-mode text
  detection block.
- **coreaoke/routes/info.py** -- Removed `is_pi` template variable.
- **coreaoke/templates/info.html** -- Removed "Expand Raspberry Pi filesystem"
  section and `is_pi` conditional. Shutdown section now checks `is_linux` only.
- **coreaoke/templates/splash.html** -- Removed `hostap_info` references.
- **tests/unit/test_get_platform.py** -- Removed `TestIsRaspberryPi` class and
  all `is_raspberry_pi` patches from remaining tests.

## Snap name and string audit (obiraoke -> coreaoke)

Verified that all snap packaging files and Python source use the coreaoke name
consistently. No obiraoke references remain in:

- **snap/snapcraft.yaml** -- `name: coreaoke`, app stanzas `coreaoke` and
  `coreaoke-server`, description text, and all `snap set coreaoke` examples.
- **snap/local/wrapper** -- `exec "$SNAP/bin/coreaoke"`, environment variables
  prefixed `COREAOKE_`, and `snapctl get` calls referencing coreaoke.
- **snap/hooks/configure** -- `snapctl start/stop` references use
  `$SNAP_INSTANCE_NAME.coreaoke-server`.
- **snap/hooks/install** -- Directory paths use `coreaoke-songs` and
  `coreaoke.log`.
- **coreaoke/*.py** -- No user-visible strings (logging, errors, warnings)
  reference obiraoke.

The `command: bin/wrapper` in both app stanzas is intentional. The wrapper
handles PulseAudio setup, snap configuration key reading, daemon log rotation,
and headless defaults before exec'ing `$SNAP/bin/coreaoke`. Bypassing the
wrapper by setting `command: bin/coreaoke` directly would break snap
configuration and audio.

## Extended snap set interface

Added runtime configuration keys to the snap set interface so users can
customize playback, branding, network, and daemon behavior without editing
config files.

**Boolean keys** (added to wrapper as `--flag` when set to `true`):

- `normalize-audio`, `disable-score`, `high-quality`, `prefer-hostname`,
  `disable-bg-music`, `disable-bg-video`, `show-splash-clock`, `hide-url`

**Value keys** (added to wrapper as `--key value` when set):

- `volume`, `bg-music-volume`, `splash-delay`, `screensaver-timeout`,
  `bg-video-path`, `bg-music-path`, `logo-path`
- `admin-password` and `streaming-format` already existed and were verified.

**Validation** (in configure hook):

- `volume` and `bg-music-volume`: must be a number between 0 and 1.
- `splash-delay` and `screensaver-timeout`: must be a non-negative integer.

**snapcraft.yaml description** updated to document all keys grouped into
Playback, Branding, Network, and Daemon categories with examples.

## Install hook pre-populates snap configuration defaults

Added `snapctl set` calls to `snap/hooks/install` so all snap configuration
keys have default values immediately after install. This means `snapctl get`
returns a value for every supported key without the user needing to set them
first.

**Keys set with defaults:**

- `port=5555`, `volume=0.85`, `bg-music-volume=0.3`, `splash-delay=2`,
  `screensaver-timeout=300`, `headless=true`, `autostart=false`,
  `streaming-format=hls`, `normalize-audio=false`, `disable-score=false`,
  `high-quality=false`, `prefer-hostname=false`, `disable-bg-music=false`,
  `disable-bg-video=false`, `show-splash-clock=false`, `hide-url=false`

**Keys intentionally left unset** (no sensible default):

- `admin-password`, `proxy`, `download-path`

## Preseed URL snap configuration key

Added a `preseed-url` snap configuration key that downloads and extracts a song
tarball on first run. The wrapper script (`snap/local/wrapper`) reads the key
with `snapctl get preseed-url` and, if set and `$SNAP_COMMON/.preseed-done` does
not exist, downloads the tarball with `curl`, extracts it into
`$SNAP_COMMON/coreaoke-songs/`, and touches the sentinel file. Subsequent starts
skip the download. To re-trigger preseed, delete `$SNAP_COMMON/.preseed-done`.

The install hook sets `preseed-url=""` as a default. The configure hook comment
block lists it as an accepted key. The `snapcraft.yaml` description documents
it under a Preseed section.

Usage: `snap set coreaoke preseed-url=https://your.server/songs.tar.gz`

## Theme snap set key

Added a `theme` snap configuration key that applies a named preset of branding
assets. Setting `snap set coreaoke theme=<name>` checks for
`$SNAP_COMMON/themes/<name>/` and, if it exists, sets `logo-path`,
`bg-video-path`, and `bg-music-path` to the corresponding files in that
directory.

The install hook creates `$SNAP_COMMON/themes/default/` and copies the built-in
assets into it:

- `$SNAP/coreaoke/static/images/logo.png` to `logo.png`
- `$SNAP/coreaoke/static/video/the_drive_by_visualdon.mp4` to `bg-video.mp4`
- `$SNAP/coreaoke/static/music/` contents to `bg-music/`

Directories are set to 0755 and files to 0644. The install hook also sets
`theme=default` so the branding paths are configured out of the box.

The configure hook validates the theme directory exists and exits with an error
if it does not. If the theme is valid, it sets the three branding keys
automatically. Custom themes can be added by creating a new directory under
`$SNAP_COMMON/themes/` with the same file layout as the default theme.

## Removed set -e from snap shell scripts

Removed `set -e` from `snap/hooks/install`, `snap/hooks/configure`, and
`snap/local/wrapper`. `set -e` causes the shell to exit silently on any
non-zero return code, including intentional test conditions like `|| true`
guards and case-statement validation patterns. All three scripts already use
explicit error handling (validation with `exit 1`, `|| true` fallbacks). The
`set -e` was actively harmful: in the configure hook, `snapctl get` calls
guarded with `|| true` could still trigger unexpected exits depending on shell
implementation details. Each file now has a comment block explaining why
`set -e` must not be re-added.

## Install hook theme asset copy paths

The `cp` commands in `snap/hooks/install` that copy built-in theme assets
referenced `$SNAP/coreaoke/static/...` but the Python package is installed at
`$SNAP/lib/python3.12/site-packages/coreaoke/`, not `$SNAP/coreaoke/`. Fixed all
three `cp` commands to use the correct path prefix:
`$SNAP/lib/python3.12/site-packages/coreaoke/static/...`. Also added
`2>/dev/null || true` to the music glob copy so a missing or empty music
directory does not cause the install hook to fail.

## Logo route graceful fallback

The `/logo` route in `coreaoke/routes/images.py` passed `k.logo_path` directly
to `send_file` without checking whether the file exists. If the configured path
pointed to a missing file (e.g. a theme asset not yet copied), Flask raised a
`FileNotFoundError` and returned a 500 error.

The route now checks `os.path.exists()` on the configured path. If the file is
missing, it falls back to the built-in static logo at
`coreaoke/static/images/logo.png` and logs a warning.

## Background video route graceful fallback

The `/stream/bg_video` route in `coreaoke/routes/stream.py` checked whether
`k.bg_video_path` was not `None` but did not verify the file existed on disk.
If the configured path pointed to a missing file, `send_file` raised a
`FileNotFoundError` and returned a 500 error.

The route now checks both `file_path is not None` and `os.path.exists()`. If
the path is set but the file does not exist, it logs a warning and returns a
404 instead of crashing.

## Sidebar navigation replaces horizontal navbar

The horizontal navbar in `coreaoke/templates/base.html` was replaced with a
collapsible pinned sidebar. The sidebar is 52px wide when collapsed (icons only)
and 208px when expanded (icons + labels). Users can pin it open via a toggle
button; the pinned state persists in `localStorage`. On hover the sidebar
temporarily expands if not pinned.

The old navbar CSS (`.navbar`, `.navbar-brand`, `.navbar-menu`, `.navbar-end`,
`.navbar-item`, `.navbar-burger`) was removed from `coreaoke/static/coreaoke.css`
and replaced with sidebar styles (`.sidebar`, `.sidebar-item`,
`.sidebar-active`, etc.). The body element uses `display: flex; flex-direction: row`
to accommodate the fixed sidebar alongside the main content area.

The current-user display and notification divs were moved from the navbar into
the main-content area. The splash screen (`coreaoke/templates/splash.html`) was
not affected -- it has its own layout and extends `base.html` via `{% block body %}`.

## Full layout redesign: sidebar-as-control-panel + inline player

Replaced the two-panel (sidebar + full-width content) layout with a new design
where the sidebar IS the control panel and the right side is a permanent player.

**Layout concept:**

- LEFT PANEL (sidebar): 52px collapsed (icons only), 224px expanded (icons +
  full page content). All page content -- search form, queue list, browse
  library, info -- renders INSIDE the sidebar when expanded.
- RIGHT PANEL (player): Full-screen, always visible. Shows background video,
  logo/mascot, now-playing overlay, QR code. The user never navigates away
  from the player.

**CSS changes (`coreaoke/static/coreaoke.css`):**

- Removed `.main-content`, `.main-content-collapsed`, `.main-content-expanded`
  classes entirely.
- `.sidebar-expanded` width changed from 208px to 224px.
- Added `.sidebar::before` -- 4px Ubuntu Orange (#e95420) accent bar on left edge.
- Added `.sidebar-logo` (32px, visible when expanded) and `.sidebar-title`
  ("Coreaoke" text, visible when expanded).
- Added `.sidebar-content` -- `display: none` when collapsed, `display: block`
  when expanded, with `flex: 1; overflow-y: auto; padding: 1rem`.
- `.sidebar-label` changed from opacity transition to `display: none/inline`.
- `.sidebar-version` set to `display: none` when collapsed.
- Added `.player-panel` -- `position: fixed; left: 52px` (default) /
  `left: 224px` (expanded); contains bg video, logo, now-playing, QR overlays.
- Added compact sidebar content styles: headings at 1rem, inputs at 0.8rem,
  tables at 0.75rem, cards/buttons scaled down for 224px width.

**Template changes (`coreaoke/templates/base.html`):**

- Replaced `#main-content` div with `#sidebar-content` div inside the sidebar.
  `{% block content %}` now renders inside the sidebar.
- Added `#player-panel` div with player markup extracted from `splash.html`:
  background video, logo image, now-playing overlay, QR code, up-next overlay.
- Player panel uses socket.io `now_playing` events for live updates.
- Sidebar toggle JS updated: expand/collapse now adjusts `player-panel` left
  offset instead of `main-content`.
- Logo (from `static/images/logo.png`) and app name "Coreaoke" added to sidebar
  header, visible when expanded.

**Context processor (`coreaoke/app.py`):**

- Added `inject_player_vars()` context processor providing `player_url`,
  `player_hide_url`, and `player_has_bg_video` to all templates so the player
  panel in base.html can render without route-specific variables.

**Page template changes:**

- `home.html`: removed `is-size-3`/`is-size-4` classes, removed `max-width`
  constraint on control box, stacked volume controls for narrow width.
- `queue.html`: stacked add-random and clear-all controls vertically.
- `search.html`: stacked search/add-to-queue buttons below input, replaced
  wide message article with compact help text.
- `files.html`: shortened sort labels ("Alphabetical" / "By Date"), shortened
  edit button text.
- `info.html`: reduced QR image from 300px to 150px, removed max-width on
  password input.

## Sidebar toggle icon, advertised URL, and splash standalone (fix-sidebar-toggle-url)

**Sidebar toggle icon (`base.html`):**

- Replaced the `icon-menu` fontello hamburger icon on the sidebar pin button
  with an inline SVG panel icon that better represents sidebar expand/collapse.
  The sidebar toggle JS (expand/collapse via `#sidebar-pin` click) was already
  correctly wired; `#sidebar-content` visibility is driven by the
  `.sidebar-expanded` CSS class on the parent `#sidebar` element.

**Advertised URL (`karaoke.py`):**

- Changed the startup log message from `Connect the player host to:
  {url}/splash` to `Connect to the web UI at: {url}/`. The root URL loads the
  web UI for singers. The `/splash` route is for dedicated TV/player screens
  only and should not be the default advertised URL. `get_url()` already
  returns `http://host:port` without a path suffix; only the log line was wrong.

**Splash standalone template (`splash.html`):**

- Removed `{% extends 'base.html' %}` and converted splash.html into a fully
  standalone HTML document. The splash screen is for dedicated TV/player screens
  and must never render the sidebar or any base.html UI chrome. All required
  head assets (jQuery, Socket.IO, fonts, CSS) are now included directly.
  The `blank_page=True` variable previously passed from the splash route
  suppressed the sidebar in base.html, but extending base.html at all was
  incorrect for a fullscreen player page.

## Sidebar toggle broken (pin button does not expand)

**Root cause:** The sidebar JS used two competing classes (`sidebar-collapsed`
and `sidebar-expanded`) for width control. On page load the HTML started with
`sidebar-collapsed` on `#sidebar`, and `expand()` removed it while adding
`sidebar-expanded` -- but `collapse()` re-added `sidebar-collapsed`, creating a
class-toggle war. Additionally, `#sidebar-content` visibility relied entirely on
the CSS rule `.sidebar-expanded .sidebar-content { display: block }`, which was
fragile and failed when the class swap did not complete cleanly.

**Fix (base.html JS):**

- Removed all references to `sidebar-collapsed` class from JS.
- `expand()` now: adds `sidebar-expanded` to `#sidebar`, adds
  `player-panel-expanded` to `#player-panel`, and explicitly sets
  `#sidebar-content` style to `display:block`.
- `collapse()` now: removes `sidebar-expanded` from `#sidebar`, removes
  `player-panel-expanded` from `#player-panel`, and explicitly sets
  `#sidebar-content` style to `display:none`.
- Pin button click toggles pinned state, saves to localStorage, and calls
  `expand()` or `collapse()`.
- Hover expand/collapse (when not pinned) calls the same functions.

**Fix (coreaoke.css):**

- `.sidebar` default width set to `52px` (was relying on `.sidebar-collapsed`).
- Removed `.sidebar-collapsed` rule entirely; only `.sidebar-expanded` overrides
  to `224px`.
- Transition changed to `0.25s ease` on both sidebar and player panel.
- Added `z-index: 1` to `.player-panel`.
- `.sidebar-collapsed .sidebar-header` selector updated to
  `.sidebar:not(.sidebar-expanded) .sidebar-header`.

**Fix (base.html HTML):**

- Removed `sidebar-collapsed` from the initial `#sidebar` class attribute.

## jQuery SPA navigation conflict (base.html)

**Root cause:** When `spa-navigation.js` re-executes page scripts during SPA
navigation, jQuery can lose its prototype methods. The inline `$(document).ready()`
block in `base.html` then throws `$(...).hide is not a function` errors, which
crash the rest of the page JS including the sidebar toggle.

**Fix (base.html script block):**

- Wrapped the entire `$(document).ready()` block in an IIFE that receives
  `jQuery` as `$`: `(function($) { ... })(jQuery);`. This guarantees `$` always
  refers to the real jQuery object regardless of SPA re-execution timing.
- Added an early guard (`if (!$ || !$.fn) return;`) so the block exits silently
  if jQuery is not fully loaded.
- Wrapped `$("#notification-alt").hide()` and all other jQuery selector calls
  outside the sidebar and player IIFEs in try/catch blocks so a failure in one
  call does not prevent the rest of the ready block from executing.
- The sidebar toggle IIFE (vanilla JS) was left unchanged.

## Sidebar UX defaults and layout

The sidebar defaulted to collapsed on first visit because the localStorage check
required an explicit `'true'` value. Users had to discover and click the pin
button before seeing any sidebar content.

**Fix (base.html):** Changed the pinned check from
`localStorage.getItem('sidebar-pinned') === 'true'` to
`localStorage.getItem('sidebar-pinned') !== 'false'`. The sidebar now starts
expanded unless the user has explicitly unpinned it.

**Fix (coreaoke.css):** Changed sidebar expanded width from a fixed 224px to
`25vw` with `min-width: 200px` and `max-width: 320px`. The player panel left
offset uses `clamp(200px, 25vw, 320px)` to stay in sync. Collapsed width
remains 52px.

**Fix (files.html):** Changed the `#alpha-bar` from a horizontal flex row
(`display: flex; justify-content: space-between`) to a vertical column layout
(`flex-direction: column; gap: 2px`) with each letter link as a block element.
This fits the narrow sidebar context where a horizontal row overflows.

## Sidebar nav links trigger full-page flash/zoom via SPA interceptor

Clicking sidebar nav links caused a visible flash and zoom because
`spa-navigation.js` intercepted the clicks and performed a full SPA content
swap (replacing `.box`), which is incorrect for sidebar links that should only
update `#sidebar-content`.

**Root cause:** `spa-navigation.js` intercepts all `a[href]` clicks via a
delegated handler on `document`. The sidebar nav links had no exclusion marker,
so the SPA system captured them before any sidebar-specific handler could act.

**Fix (base.html):**
1. Added `no-spa` class to all sidebar nav `<a>` tags so `spa-navigation.js`
   skips them in its `shouldExcludeLink()` check.
2. Added `data-sidebar-link="true"` attribute to each sidebar nav link.
3. Added a new IIFE after the sidebar toggle logic that attaches direct click
   listeners to `[data-sidebar-link]` elements. These listeners call
   `e.preventDefault()` and `e.stopPropagation()`, then use `fetch()` to load
   the target page, extract the new `#sidebar-content` from the response, and
   replace the current sidebar content via `innerHTML`. The handler also calls
   `history.pushState()` and updates the `sidebar-active` class.

## Selectize and inline scripts not initializing after sidebar AJAX navigation

After sidebar AJAX navigation, page-specific JavaScript (selectize dropdowns,
socket.io handlers, etc.) did not initialize because the browser does not
execute `<script>` tags inserted via `innerHTML`.

**Root cause:** `loadSidebarContent()` in `base.html` replaced
`#sidebar-content` using `innerHTML`, which inserts script elements as inert
HTML nodes. The browser only executes scripts added to the DOM via
`document.createElement('script')` followed by a DOM insertion.

**Fix (base.html):**
After setting `sc.innerHTML = newContent.innerHTML`, added a loop that finds
all `<script>` elements in the loaded content, clones each into a fresh
`<script>` element (preserving attributes and textContent), and replaces the
inert node with the new one. This forces the browser to evaluate each script,
re-initializing selectize, socket.io handlers, and other page-specific JS.

## QR code route FileNotFoundError at startup

The `/qrcode` route in `coreaoke/routes/images.py` called `send_file()` on
`k.qr_code_path` without checking whether the file exists. At startup the QR
code has not been generated yet, causing a `FileNotFoundError`.

**Fix:** Added a guard identical to the logo route pattern: if
`k.qr_code_path` is falsy or the file does not exist, return an empty 404
instead of crashing.

## Snap download path not reading COREAOKE_SONGS_DIR

`get_default_dl_dir()` in `coreaoke/lib/get_platform.py` constructed the snap
download path from `SNAP_COMMON` but ignored the `COREAOKE_SONGS_DIR`
environment variable that `snap/local/wrapper` explicitly exports. If
`SNAP_COMMON` was unset or resolved incorrectly, yt-dlp would attempt to
create `/var/snap/coreaoke` (the fallback minus the `coreaoke-songs` suffix)
and fail with permission denied.

**Fix:** `get_default_dl_dir()` now checks `COREAOKE_SONGS_DIR` first. If
the wrapper already set the canonical songs directory, that value is returned
directly, bypassing the `SNAP_COMMON` construction entirely.

## Selectize not initializing on sidebar-injected content

Re-executing `<script>` tags after sidebar AJAX navigation was not sufficient
to initialize selectize dropdowns. Selectize binds to elements during
`DOMContentLoaded`, which has already fired by the time sidebar content is
injected via `innerHTML`.

**Fix:** Replaced the basic `setTimeout` selectize init in `loadSidebarContent()`
with a more robust approach (200 ms delay for slower devices):
- Uses `select:not(.selectized)` selector to skip already-initialized elements.
- Applies specific options for `#song_query` (create: false, sortField, maxOptions,
  placeholder).
- Wraps each init in try/catch with a `console.warn` fallback.
- Unlocks plain `input[type="text"]` elements that may be left disabled/readonly
  after AJAX injection.

## Search page bypass for sidebar AJAX navigation

The `/search` page uses selectize with complex socket.io-dependent initialization
that cannot survive AJAX injection into the sidebar. When `loadSidebarContent()`
loaded `/search` via fetch/innerHTML, selectize bindings and socket.io event
listeners failed to initialize properly because they depend on a full page load
lifecycle.

**Fix:** Added an early return in `loadSidebarContent()` that performs a normal
`window.location.href` navigation instead of AJAX loading for:
- The `/search` URL exactly.
- Any URL containing `?query=` (search results pages that also rely on selectize).

## Search help text too small in sidebar

The compact sidebar content styles reduced font sizes aggressively for tables
and buttons but did not set an explicit font-size for `p`, `.is-italic`, `em`,
and `i` elements. These inherited a smaller size from parent rules, making the
search help text unreadable at sidebar width.

**Fix:** Added an explicit rule in `coreaoke.css` setting `font-size: 0.85rem`
for `.sidebar-content p`, `.sidebar-content .is-italic`, `.sidebar-content em`,
and `.sidebar-content i`. This is readable at sidebar width without being too
large.

## Player panel not playing songs (missing splash screen registration)

The embedded player panel in `base.html` connects to socket.io but never
registers as a splash screen client. The server requires clients to emit
`register_splash` before it will stream video to them. The old standalone
`splash.html` did this via `splash.js`, but the new `base.html` player panel
did not replicate the registration.

**Root cause:** `connectSocket()` in `base.html` called `io()` and listened
for `connect`/`disconnect` but never emitted `register_splash`. Without
registration the server never assigned a splash role and the client had no
video element or HLS wiring to play the stream.

**Fix:** Three changes in `base.html`:

1. Added `window.socket.emit('register_splash')` inside the socket `connect`
   handler and a `splash_role` listener so the server recognises the panel as a
   splash screen client.
2. Added a `<video id="player-video">` element inside `#player-panel` for
   karaoke playback, separate from the existing background video.
3. Extended the `now_playing` socket handler to set the video source URL, use
   HLS.js for `.m3u8` streams, call `play()`, and toggle visibility between
   the background video (idle) and the karaoke video (playing). Also wired up
   `pause`, `play`, `skip`, `volume`, `restart`, and `playback_position`
   socket events to the player panel video element.

## Sidebar footer version string invisible

The `.sidebar-version` rule used `font-size: 0.625rem` and
`color: rgba(255,255,255,0.3)` with `display: none`, making the version string
invisible even when the sidebar was expanded (the `sidebar-expanded` override
only toggled `display: inline`). The fix bumps font size to `0.7rem`, lightens
the colour to `rgba(255,255,255,0.4)`, sets `display: block` as the base state,
and adds `overflow: hidden` and `padding: 0.5rem 0.75rem` for proper layout.

## Removed Shutdown section from info page

The Shutdown section in `coreaoke/templates/info.html` contained Quit Coreaoke,
Reboot System, and Shutdown System buttons along with a warning about proper
shutdown. The entire section (heading, card, buttons, and warning text) was
removed. The associated JavaScript click handlers for `#quit-link`,
`#shutdown-link`, and `#restart-link` were also removed since they no longer
have corresponding DOM elements.

## yt-dlp snap confinement log level downgraded to info

The log message in `coreaoke/lib/youtube_dl.py` `upgrade_youtubedl()` that fires
when yt-dlp self-upgrade is skipped inside snap confinement was changed from
`logging.warning()` to `logging.info()`. This is expected behavior inside a
snap, not a warning condition -- upgrades are handled by `snap refresh`.

## Snap lint ignore rules for library warnings

Added a `lint.ignore` section to `snap/snapcraft.yaml` to suppress two
library warnings from `snapcraft pack`:

- `usr/lib/x86_64-linux-gnu/liboss4-salsa.so.2.0.0`
- `usr/lib/x86_64-linux-gnu/libasound.so.2.0.0`

Both libraries are loaded at runtime via `dlopen` by ALSA plugins and are not
detected by the static dependency linter. The lint ignore rules prevent false
positive warnings without excluding the libraries from the snap.

## Sidebar content text too small

Body text inside `.sidebar-content` (paragraphs, list items, table cells, and
spans) rendered at various small sizes making the sidebar hard to read. A new
grouped rule sets these elements to `0.875rem`. A companion rule bumps
`.is-size-7` and `small` inside the sidebar to `0.8rem !important` so they
remain legible.

## Yellow/gold button and text colors replaced with spec colors

The CSS and templates used Bulma-style `is-warning` amber (#f99b11) for buttons,
tags, notifications, progress bars, and text. These yellow/gold colors are not
in the spec palette. All `is-warning` component styles in `coreaoke.css` now use
#e95420 (Ubuntu Orange) for backgrounds and #ffffff for text. The
`.has-text-warning` helper class now renders as `rgba(255,255,255,0.7)` instead
of amber. Inline `has-text-warning` overrides in `splash.html` and `info.html`
were updated to match. The Search button (`is-warning`) and Add to queue button
(`is-info`) in `search.html` were changed to `is-primary` (#e95420).

## Credits page

Added `/credits` route with a Credits & Acknowledgements page accessible from
the sidebar nav. Lists upstream projects (PiKaraoke, yt-dlp, FFmpeg, Flask,
Socket.IO, Selectize.js, HLS.js, Fontello, Ubuntu Variable Font), Ubuntu
Coreaoke contributors, and Ubuntu Core. Visiting the page emits a
`credits_overlay` socket event that displays a 5-second overlay on the player
panel. Blueprint registered in `app.py` as an internal (non-API) route.

## Button colors updated to Vanilla Framework spec

Primary/positive action buttons (`.button.is-primary`, `.button.is-success`,
`.button.is-warning`) now use Vanilla Framework green `#0e8420` with hover
`rgb(11, 108, 26)` instead of Ubuntu Orange. Destructive buttons
(`.button.is-danger`) keep `#c7162b` with hover updated to `rgb(176, 19, 38)`.
Ubuntu Orange `#e95420` is now reserved for sidebar active-item left border,
sidebar active-item background tint, and the pin button when pinned.
