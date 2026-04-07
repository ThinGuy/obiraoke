"""Credits page route."""

from flask import abort, render_template
from flask_smorest import Blueprint

from coreaoke.lib.branding import get_lockdown
from coreaoke.lib.current_app import get_karaoke_instance, get_site_name

credits_bp = Blueprint("credits", __name__)


@credits_bp.route("/credits")
def credits():
    """Render the credits and acknowledgements page."""
    if get_lockdown():
        abort(403)
    k = get_karaoke_instance()
    if k.socketio:
        k.socketio.emit("credits_overlay", namespace="/")
    return render_template(
        "credits.html",
        site_title=get_site_name(),
    )
