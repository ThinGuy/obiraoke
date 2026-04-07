"""Credits page route."""

from flask import abort, render_template
from flask_smorest import Blueprint

from coreaoke import VERSION
from coreaoke.lib.branding import get_lockdown
from coreaoke.lib.current_app import get_karaoke_instance, get_site_name
from coreaoke.routes.info import _gather_system_info

credits_bp = Blueprint("credits", __name__)


@credits_bp.route("/credits")
def credits():
    """Render the credits and acknowledgements page."""
    if get_lockdown():
        abort(403)
    k = get_karaoke_instance()
    if k.socketio:
        k.socketio.emit("credits_overlay", namespace="/")

    system_info = _gather_system_info()

    return render_template(
        "credits.html",
        site_title=get_site_name(),
        platform=k.platform,
        os_version=k.os_version,
        ffmpeg_version=k.ffmpeg_version,
        is_transpose_enabled=k.is_transpose_enabled,
        youtubedl_version=k.youtubedl_version,
        coreaoke_version=VERSION,
        system_info=system_info,
    )
