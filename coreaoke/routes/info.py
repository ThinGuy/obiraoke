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


def _run_cmd(cmd: list[str]) -> str | None:
    """Run a command and return stdout, or None on failure."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip() or result.stderr.strip() or None
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None


def _gather_system_info() -> dict:
    """Gather extended system information for the info page."""
    data: dict = {}

    # snapd via dpkg
    snapd_dpkg_line = _run_cmd(
        ["dpkg-query", "-W", "-f", "${Status} ${Package} ${Version}\n", "snapd"]
    )
    if snapd_dpkg_line is None:
        raw = _run_cmd(["dpkg", "-l", "snapd"])
        if raw:
            for line in raw.splitlines():
                if line.startswith("ii"):
                    snapd_dpkg_line = line
                    break
    if snapd_dpkg_line and snapd_dpkg_line.startswith("ii"):
        parts = snapd_dpkg_line.split()
        data["snapd_dpkg"] = {
            "status": parts[0] if len(parts) > 0 else None,
            "package": parts[1] if len(parts) > 1 else None,
            "version": parts[2] if len(parts) > 2 else None,
        }
    elif snapd_dpkg_line and "install ok installed" in snapd_dpkg_line:
        parts = snapd_dpkg_line.split()
        data["snapd_dpkg"] = {
            "status": "ii",
            "package": parts[-2] if len(parts) >= 2 else "snapd",
            "version": parts[-1] if len(parts) >= 1 else None,
        }
    else:
        data["snapd_dpkg"] = None

    # snapd via snap list
    snapd_snap_raw = _run_cmd(["snap", "list", "snapd"])
    if snapd_snap_raw:
        lines = snapd_snap_raw.strip().splitlines()
        last = lines[-1] if lines else ""
        parts = last.split()
        if parts and parts[0] == "snapd":
            data["snapd_snap"] = {
                "name": parts[0],
                "version": parts[1] if len(parts) > 1 else None,
            }
        else:
            data["snapd_snap"] = None
    else:
        data["snapd_snap"] = None

    # Check if Ubuntu
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

        # Ubuntu Pro client version via dpkg
        pro_raw = _run_cmd(["dpkg", "-l", "ubuntu-pro-client"])
        pro_version = None
        if pro_raw:
            for line in pro_raw.splitlines():
                if line.startswith("ii"):
                    parts = line.split()
                    pro_version = parts[2] if len(parts) > 2 else None
                    break
        data["pro_client_version"] = pro_version

        # Ubuntu Pro attached status
        pro_status_raw = _run_cmd(["pro", "status", "--format", "json"])
        if pro_status_raw:
            try:
                pro_json = json.loads(pro_status_raw)
                attached = pro_json.get("attached", False)
                data["pro_attached"] = "Attached" if attached else "Not Attached"
            except (json.JSONDecodeError, KeyError):
                data["pro_attached"] = None
        else:
            data["pro_attached"] = None

        # Available updates
        updates_raw = _run_cmd(
            ["/usr/lib/update-notifier/apt-check"]
        )
        if updates_raw:
            # apt-check outputs to stderr: "total;security"
            parts = updates_raw.split(";")
            if len(parts) == 2:
                try:
                    total = int(parts[0])
                    security = int(parts[1])
                    data["available_updates"] = f"{total} updates ({security} security)"
                except ValueError:
                    data["available_updates"] = updates_raw
            else:
                data["available_updates"] = updates_raw
        else:
            # Try human-readable fallback
            updates_hr = _run_cmd(
                ["/usr/lib/update-notifier/apt-check", "--human-readable"]
            )
            data["available_updates"] = updates_hr
    else:
        data["os_release"] = None
        data["pro_client_version"] = None
        data["pro_attached"] = None
        data["available_updates"] = None

    return data


def _parse_os_release() -> dict | None:
    """Parse /etc/os-release into a dict."""
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


@info_bp.route("/info")
def info():
    """System information and settings page."""
    k = get_karaoke_instance()
    site_name = get_site_name()
    url = k.url
    admin_password = get_admin_password()
    is_linux = get_platform() == "linux"

    preferred_language = k.preferences.get("preferred_language", "en")
    # youtube-dl
    youtubedl_version = k.youtubedl_version

    system_info = _gather_system_info()

    return render_template(
        "info.html",
        site_title=site_name,
        title="Settings",
        url=url,
        admin=is_admin(),
        admin_password=admin_password,
        platform=k.platform,
        os_version=k.os_version,
        ffmpeg_version=k.ffmpeg_version,
        is_transpose_enabled=k.is_transpose_enabled,
        youtubedl_version=youtubedl_version,
        coreaoke_version=VERSION,
        cpu=None,
        memory=None,
        disk=None,
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
        system_info=system_info,
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
