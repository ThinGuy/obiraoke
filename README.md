# Ubuntu Coraoke

![Ubuntu Coraoke](coraoke-splash.png)

## Table of Contents

- [Credit / Thanks](#credit--thanks)
- [About](#about)
- [Features](#features)
- [Screenshots](#screenshots)
- [Supported Devices / OS / Platforms](#supported-devices--os--platforms)
- [Installing / Upgrading / Removing](#installing--upgrading--removing)
- [Usage](#usage)
- [Help / Options](#helpoptions)

## Credit / Thanks

I wanted to let the original author know that this has been one of my favorite projects on GitHub. While I've always used a cloud-init script with LXD Profiles to get this going in less than 60 seconds, I've recently realized the beauty of Snaps and thought this was a perfect fit.

I want to be perfectly clear: while I have forked, repackaged, added snapd controls, and changed some graphics, that is just window dressing. The person who deserves *all of the credit* is [vicwomg](https://github.com/vicwomg), who ensures that this project is independently maintained and free for everyone to enjoy.

If this software has made your life better, eliminated male patterned baldness, was responsible for Trump getting perp-walked out of the White House, or you'd just like to help keep the project alive and growing, feel free to [buy Vic a coffee](https://www.buymeacoffee.com/vicwomg)!

<a href="https://www.buymeacoffee.com/vicwomg" target="_blank"><img src="https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png" alt="Buy Me A Coffee" style="height: 41px !important;width: 174px !important;"></a>

## About

Ubuntu Coraoke is a strictly-confined snap implementation of [vicwomg](https://github.com/vicwomg)'s [PiKaraoke](https://github.com/vicwomg/pikaraoke), targeting Ubuntu Core, Ubuntu, and any Linux with [Snapd](https://snapcraft.io/snapd).

[PiKaraoke](https://github.com/vicwomg/pikaraoke) brings a fun and professional "KTV" experience to any home, office, or colonoscopy examination room.

Any platform that can run Snapd instantly becomes a full-featured karaoke station with:

- A full-screen player and an instant web interface
- Easy access via QR code or by visiting `http://<hostname>:5555` on any modern browser
- A client-free experience — browse your local library, manage the queue, and access countless karaoke hits from YouTube, all from the Ubuntu Coraoke web UI on any device with a modern browser

## Features

- 📱 **Instant Mobile Remote:** Search and queue songs from any smartphone — just scan and sing.
- 📺 **Dedicated Player:** Full-screen splash screen that can be opened on any web browser for a true karaoke room feel.
- 🌐 **YouTube & Local Media:** Play your own files or access more from the web.
- 🎹 **Live Pitch Shifting:** Adjust the key of any song to match your vocal range.
- 🛠️ **Admin Control:** Manage the queue and settings via a password-protected admin mode.
- 🎯 **Hyper-accurate vocal performance scoring system:** (not really, it's random — but kind of fun!)
- 🐧 **Lightweight & Versatile:** Runs anywhere from a Raspberry Pi to a high-end PC.

## Screenshots

<div style="display: flex; flex-wrap: wrap; gap: 8px;">
<img width="250" alt="coraoke-nowplaying" src="https://user-images.githubusercontent.com/4107190/95813193-2cd5c180-0ccc-11eb-89f4-11a69676dc6f.png">
<img width="250" alt="coraoke-queue" src="https://user-images.githubusercontent.com/4107190/95813195-2d6e5800-0ccc-11eb-8f00-1369350a8a1c.png">
<img width="250" alt="coraoke-browse" src="https://user-images.githubusercontent.com/4107190/95813182-27787700-0ccc-11eb-82c8-fde7f0a631c1.png">
<img width="250" alt="coraoke-search1" src="https://user-images.githubusercontent.com/4107190/95813197-2e06ee80-0ccc-11eb-9bf9-ddb24d988332.png">
<img width="250" alt="coraoke-search2" src="https://user-images.githubusercontent.com/4107190/95813190-2ba49480-0ccc-11eb-84e3-f902cbd489a2.png">
<img width="400" height="300" alt="coraoke-tv" src="https://user-images.githubusercontent.com/4107190/95813564-019fa200-0ccd-11eb-95e1-57a002c357a3.png">
</div>

## Supported Devices / OS / Platforms

Ubuntu Coraoke is a strictly-confined snap that runs directly on Ubuntu Core or on any platform with Snapd installed.

Check [here](https://snapcraft.io/docs/tutorials/install-the-daemon/) for any distributions added since this guide was last updated.

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

Installation is done via the [Snap Store](https://snapcraft.io/).

### Installation

```sh
sudo snap install coraoke
```

### Upgrading

```sh
sudo snap refresh coraoke
```

### Removing while preserving song library

```sh
sudo snap remove coraoke
```

### Removing and purging all downloaded content

```sh
sudo snap remove coraoke --purge
```

## Usage

Run coraoke from the command line:

```sh
coraoke
```

Launches the player in "headed" mode via your default browser. Scan the QR code to connect mobile remotes.

Use `coraoke --headless` to run as a background server for external browsers.

- Set Ubuntu Coraoke to autostart in headless mode: `sudo snap set coraoke autostart=true`
- Ubuntu Coraoke is available at `http://localhost:5555` on the device it was installed on.

### Snap Configuration

Ubuntu Coraoke can be configured via `snap set` without touching the command line:

| Key | Description | Example |
|-----|-------------|---------|
| `port` | HTTP listen port (default: 5555) | `sudo snap set coraoke port=8080` |
| `admin-password` | Lock down admin features | `sudo snap set coraoke admin-password=secret` |
| `download-path` | Custom songs directory | `sudo snap set coraoke download-path=/mnt/songs` |
| `log-level` | Logging verbosity | `sudo snap set coraoke log-level=DEBUG` |
| `headless` | Run without local browser | `sudo snap set coraoke headless=true` |
| `streaming-format` | `hls` or `mp4` | `sudo snap set coraoke streaming-format=mp4` |
| `autostart` | Start on boot | `sudo snap set coraoke autostart=true` |
| `proxy` | HTTP proxy for yt-dlp | `sudo snap set coraoke proxy=http://proxy.example.com:3128` |

## Help/Options

Full help is available via:

```sh
coraoke --help
```

```
options:
  -h, --help            show this help message and exit
  -p PORT, --port PORT  Desired http port (default: 5555)
  -d DOWNLOAD_PATH [DOWNLOAD_PATH ...], --download-path DOWNLOAD_PATH [DOWNLOAD_PATH ...]
                        Desired path for downloaded songs. (default: /var/snap/coraoke/common/coraoke-songs)
  --youtubedl-proxy YOUTUBEDL_PROXY
                        Proxy server to use for youtube-dl, in case blocked by a firewall
  --ytdl-args YTDL_ARGS
                        Additional arguments to pass to youtube-dl/yt-dlp (as a single string)
  -l LOG_LEVEL, --log-level LOG_LEVEL
                        Logging level int value (DEBUG: 10, INFO: 20, WARNING: 30, ERROR: 40, CRITICAL: 50). (default: 20)
  --prefer-hostname     Use the local hostname instead of the IP as the connection URL.
  --hide-splash-screen, --headless
                        Headless mode. Don't launch the splash screen/player on the coraoke server
  --logo-path LOGO_PATH [LOGO_PATH ...]
                        Path to a custom logo image file for the splash screen. Recommended dimensions ~ 2048x1024px
  -u URL, --url URL     Override the displayed IP address with a supplied URL.
  --window-size WINDOW_SIZE
                        Desired window geometry in pixels for headed mode (Example: --window-size 800,600).
  --external-monitor    Experimental: Launch the splash screen on an external monitor.
  --admin-password ADMIN_PASSWORD
                        Administrator password for locking down queue editing, player controls, and system shutdown.
  --bg-music-path BG_MUSIC_PATH [BG_MUSIC_PATH ...]
                        Path to a directory of mp3 files for splash screen background music.
  --bg-video-path BG_VIDEO_PATH [BG_VIDEO_PATH ...]
                        Path to a background video mp4 file for the splash screen.
  --config-file-path CONFIG_FILE_PATH
                        Path to a config file (default: config.ini)
  --preferred-language PREFERRED_LANGUAGE
                        Set the preferred language. Available: en, de_DE, es_VE, fi_FI, fr_FR, id_ID, it_IT, ja_JP, ko_KR, nl_NL, no_NO, pt_BR, ru_RU, th_TH, zh_Hans_CN, zh_Hant_TW
  --enable-swagger      Enable Swagger API documentation at /apidocs.
  --streaming-format {hls,mp4}
                        Video streaming format (default: hls)
  -v VOLUME, --volume VOLUME
                        Set initial player volume, 0.0-1.0 (default: 0.85)
  -n, --normalize-audio
                        Normalize volume.
  -s SPLASH_DELAY, --splash-delay SPLASH_DELAY
                        Delay between songs on splash screen in seconds (default: 2)
  -t SCREENSAVER_TIMEOUT, --screensaver-timeout SCREENSAVER_TIMEOUT
                        Screensaver delay in seconds, 0 to disable (default: 300)
  --hide-url            Hide URL and QR code from the splash screen.
  --hide-overlay        Hide all overlays on top of video.
  --hide-notifications  Hide notifications from the splash screen.
  --show-splash-clock   Show a digital clock on the splash screen.
  --high-quality        Download higher quality video.
  -c, --complete-transcode-before-play
                        Wait for full transcoding before playback begins.
  -b BUFFER_SIZE, --buffer-size BUFFER_SIZE
                        Buffer size for transcoded video in kilobytes (default: 150)
  --disable-bg-music    Disable background music on splash screen.
  --bg-music-volume BG_MUSIC_VOLUME
                        Background music volume, 0.0-1.0 (default: 0.3)
  --disable-bg-video    Disable background video on splash screen.
  --disable-score       Disable the score screen after each song.
  --limit-user-songs-by LIMIT_USER_SONGS_BY
                        Limit songs per user in queue (default: 0 = unlimited)
  --avsync AVSYNC       AV sync offset in seconds (negative = advance audio, positive = delay audio)
  --cdg-pixel-scaling   Enable CDG pixel scaling for improved CDG file rendering.
  --mascot-mode         Enable mascot mode, overriding the splash logo and background video.
```
