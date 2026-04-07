"""Platform detection utilities for PiKaraoke."""

import os
import platform
import shutil
import sys


def is_android() -> bool:
    """Check if the current system is Android.

    Returns:
        True if running on Android, False otherwise.
    """
    return os.path.exists("/system/app/") and os.path.exists("/system/priv-app")


def is_windows() -> bool:
    """Check if the current system is Windows.

    Returns:
        True if running on Windows, False otherwise.
    """
    return sys.platform.startswith("win")


def is_macos() -> bool:
    """Check if the current system is macOS.

    Returns:
        True if running on macOS, False otherwise.
    """
    return sys.platform == "darwin"


def is_linux() -> bool:
    """Check if the current system is Linux.

    Returns:
        True if running on Linux, False otherwise.
    """
    return sys.platform.startswith("linux")


def get_installed_js_runtime() -> str | None:
    """Get the name of an installed JavaScript runtime.

    Checks for deno, node, bun, and quickjs in order of preference.
    A JS runtime is required by yt-dlp for some downloads.

    Returns:
        Name of the installed runtime ('deno', 'node', 'bun', 'quickjs'),
        or None if none is installed.
    """
    if shutil.which("deno") is not None:
        return "deno"
    if shutil.which("node") is not None:
        return "node"
    if shutil.which("bun") is not None:
        return "bun"
    if shutil.which("quickjs") is not None:
        return "quickjs"
    return None


def has_js_runtime() -> bool:
    """Check if a JavaScript runtime is installed.

    Returns:
        True if a JS runtime is available, False otherwise.
    """
    return get_installed_js_runtime() is not None


def get_platform() -> str:
    """Detect the current operating system/platform.

    Returns:
        Platform identifier string: 'osx', 'android', 'linux', 'windows',
        or 'unknown'.
    """
    if is_macos():
        return "osx"
    elif is_android():
        return "android"
    elif is_linux():
        return "linux"
    elif is_windows():
        return "windows"
    else:
        return "unknown"


def get_default_dl_dir(platform: str) -> str:
    """Get the default download directory for the given platform.

    Checks for legacy directory locations and returns those if they exist,
    otherwise returns the new default location.

    Args:
        platform: Platform identifier from get_platform().

    Returns:
        Path string for the default download directory.
    """
    songs_dir = os.environ.get("COREAOKE_SONGS_DIR")
    if songs_dir:
        return songs_dir
    if os.environ.get("SNAP"):
        return os.path.join(
            os.environ.get("SNAP_COMMON", "/var/snap/coreaoke/common"), "coreaoke-songs"
        )
    if is_windows():
        legacy_directory = os.path.expanduser("~\\pikaraoke\\songs")
        if os.path.exists(legacy_directory):
            return legacy_directory
        else:
            return "~\\coreaoke-songs"
    else:
        legacy_directory = "~/pikaraoke/songs"
        if os.path.exists(legacy_directory):
            return legacy_directory
        else:
            return "~/coreaoke-songs"


def get_os_version() -> str:
    """Get the operating system version string.

    Returns:
        OS version string from platform.version().
    """
    return platform.version()


def get_data_directory() -> str:
    """Get the writable data directory for the application.

    Determines the appropriate location for storing application data
    (config, logs, etc.) based on the operating system.

    Returns:
        Path to the data directory.
    """
    if os.environ.get("SNAP"):
        # Snap confinement: $SNAP_USER_DATA/config
        base_path = os.environ.get("SNAP_USER_DATA", os.path.expanduser("~"))
        path = os.path.join(base_path, "config")
    elif is_windows():
        # Windows: %APPDATA%/coreaoke
        base_path = os.environ.get("APPDATA")
        # Fallback if APPDATA is not set (rare, but possible)
        if not base_path:
            base_path = os.path.expanduser("~")
        path = os.path.join(base_path, "coreaoke")
    else:
        # Linux, macOS, Android: ~/.coreaoke
        path = os.path.expanduser("~/.coreaoke")

    # Ensure the directory exists
    if not os.path.exists(path):
        os.makedirs(path)

    return path


def get_bg_video_path() -> str | None:
    """Resolve the background video path using a fallback chain.

    1. $SNAP/lib/python3.12/site-packages/coreaoke/static/video/bg-video.mp4
       (only inside snap confinement)
    2. static/video/bg-video.mp4 relative to the coreaoke package
       (outside snap)
    3. None if neither exists
    """
    snap = os.environ.get("SNAP")
    if snap:
        snap_path = os.path.join(
            snap, "lib", "python3.12", "site-packages", "coreaoke", "static", "video", "bg-video.mp4"
        )
        if os.path.isfile(snap_path):
            return snap_path

    local_path = os.path.join(os.path.dirname(__file__), "..", "static", "video", "bg-video.mp4")
    if os.path.isfile(local_path):
        return local_path

    return None


def is_running_in_docker():
    """Check if we're running in a container using existence of /.dockerenv."""
    return os.path.exists("/.dockerenv")
