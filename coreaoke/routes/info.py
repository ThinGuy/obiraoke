"""System information and settings page route."""

import json
import subprocess

import flask_babel
import psutil
from flask import jsonify, render_template
from flask_smorest import Blueprint

from coreaoke import VERSION
from coreaoke.constants import LANGUAGES
from coreaoke.lib.current_app import (
    get_admin_password,
    get_karaoke_instance,
    get_site_name,
    is_admin,
)
from coreaoke.lib.get_platform import get_platform

_ = flask_babel.gettext


info_bp = Blueprint("info", __name__)


def _read_dpkg_version(package: str) -> str | None:
    """Read a package version from /var/lib/dpkg/status.

    Parses the dpkg status file directly instead of spawning dpkg or
    dpkg-query, which may not be accessible under snap strict confinement.
    """
    try:
        with open("/var/lib/dpkg/status") as f:
            in_package = False
            for line in f:
                if line.startswith("Package: ") and line.strip() == f"Package: {package}":
                    in_package = True
                elif in_package and line.startswith("Package: "):
                    in_package = False
                elif in_package and line.startswith("Version: "):
                    return line.split(":", 1)[1].strip()
                elif in_package and line.strip() == "":
                    in_package = False
    except OSError:
        pass
    return None


def _parse_os_release() -> dict | None:
    """Parse /etc/os-release into a dict.

    Reads the file directly rather than using lsb_release, which is not
    available under snap strict confinement.
    """
    try:
        with open("/etc/os-release") as f:
            result = {}
            for line in f:
                line = line.strip()
                if "=" in line:
                    key, _, value = line.partition("=")
                    result[key] = value.strip('"')
            return result
    except OSError:
        return None


def _gather_system_info() -> dict:
    """Gather extended system information for the credits page.

    All data is read from files on disk where possible to avoid subprocess
    calls that fail under snap strict confinement.
    """
    data: dict = {}

    # snapd version from dpkg status file (readable under confinement)
    snapd_version = _read_dpkg_version("snapd")
    if snapd_version:
        data["snapd_dpkg"] = {
            "status": "ii",
            "package": "snapd",
            "version": snapd_version,
        }
    else:
        data["snapd_dpkg"] = None

    # Check if Ubuntu via /etc/os-release
    os_release = _parse_os_release()
    is_ubuntu = False
    if os_release:
        os_id = os_release.get("ID", "")
        id_like = os_release.get("ID_LIKE", "")
        is_ubuntu = os_id == "ubuntu" or "ubuntu" in id_like
    data["is_ubuntu"] = is_ubuntu

    if is_ubuntu and os_release:
        data["os_release"] = {
            "PRETTY_NAME": os_release.get("PRETTY_NAME"),
            "VERSION_ID": os_release.get("VERSION_ID"),
            "VERSION_CODENAME": os_release.get("VERSION_CODENAME"),
        }

        # Ubuntu Pro client version from dpkg status file
        data["pro_client_version"] = _read_dpkg_version("ubuntu-pro-client")

        # Ubuntu Pro attached status via pro CLI (may not work in confinement)
        try:
            result = subprocess.run(
                ["pro", "status", "--format", "json"],
                capture_output=True, text=True, timeout=5,
            )
            pro_json = json.loads(result.stdout)
            attached = pro_json.get("attached", False)
            data["pro_attached"] = "Attached" if attached else "Not Attached"
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError,
                json.JSONDecodeError, KeyError):
            data["pro_attached"] = None

        # Available updates via apt-get dry-run (works in confinement)
        try:
            result = subprocess.run(
                ["apt-get", "-s", "upgrade"],
                capture_output=True, text=True, timeout=10,
            )
            inst_count = sum(
                1 for line in result.stdout.splitlines()
                if line.startswith("Inst ")
            )
            data["available_updates"] = f"{inst_count} updates" if inst_count else None
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            data["available_updates"] = None
    else:
        data["os_release"] = None
        data["pro_client_version"] = None
        data["pro_attached"] = None
        data["available_updates"] = None

    return data


@info_bp.route("/info")
def info():
    """System information and settings page."""
    k = get_karaoke_instance()
    site_name = get_site_name()
    url = k.url
    admin_password = get_admin_password()
    is_linux = get_platform() == "linux"

    preferred_language = k.preferences.get("preferred_language", "en")

    return render_template(
        "info.html",
        site_title=site_name,
        title="Settings",
        url=url,
        admin=is_admin(),
        admin_password=admin_password,
        is_linux=is_linux,
        volume=int(k.volume * 100),
        bg_music_volume=int(k.bg_music_volume * 100),
        disable_bg_music=k.disable_bg_music,
        disable_bg_video=k.disable_bg_video,
        disable_score=k.disable_score,
        hide_notifications=k.hide_notifications,
        show_splash_clock=k.show_splash_clock,
        hide_url=k.hide_url,
        hide_overlay=k.hide_overlay,
        screensaver_timeout=k.screensaver_timeout,
        splash_delay=k.splash_delay,
        normalize_audio=k.normalize_audio,
        cdg_pixel_scaling=k.cdg_pixel_scaling,
        high_quality=k.high_quality,
        complete_transcode_before_play=k.complete_transcode_before_play,
        avsync=k.avsync,
        limit_user_songs_by=k.limit_user_songs_by,
        enable_fair_queue=k.enable_fair_queue,
        buffer_size=k.buffer_size,
        languages=LANGUAGES,
        preferred_language=preferred_language,
        browse_results_per_page=k.browse_results_per_page,
        score_phrases={
            "low": k.low_score_phrases,
            "mid": k.mid_score_phrases,
            "high": k.high_score_phrases,
        },
    )


@info_bp.route("/info/stats")
def get_system_stats():
    """Get system statistics (CPU, Memory, Disk).

    Returns:
        JSON response with system stats.
    """
    if not is_admin():
        return jsonify({"error": "Unauthorized"}), 403

    # cpu
    try:
        # We can afford to block a bit here since it is async
        cpu = str(psutil.cpu_percent(interval=1)) + "%"
    except:
        cpu = _("CPU usage query unsupported")

    # mem
    memory = psutil.virtual_memory()
    available = round(memory.available / 1024.0 / 1024.0, 1)
    total = round(memory.total / 1024.0 / 1024.0, 1)
    memory_str = (
        str(available) + "MB free / " + str(total) + "MB total ( " + str(memory.percent) + "% )"
    )

    # disk
    disk = psutil.disk_usage("/")
    free = round(disk.free / 1024.0 / 1024.0 / 1024.0, 1)
    total = round(disk.total / 1024.0 / 1024.0 / 1024.0, 1)
    disk_str = str(free) + "GB free / " + str(total) + "GB total ( " + str(disk.percent) + "% )"

    return jsonify({"cpu": cpu, "memory": memory_str, "disk": disk_str})
