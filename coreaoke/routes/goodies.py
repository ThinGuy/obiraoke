"""Goodies portal route."""

from flask import abort, render_template
from flask_smorest import Blueprint

from coreaoke.lib.branding import get_lockdown
from coreaoke.lib.current_app import get_site_name

goodies_bp = Blueprint("goodies", __name__)


@goodies_bp.route("/goodies")
def goodies():
    """Render the Goodies portal page that hosts About, Docs, and SBOM."""
    if get_lockdown():
        abort(403)
    return render_template("goodies_portal.html", site_title=get_site_name())
