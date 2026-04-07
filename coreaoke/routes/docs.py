"""Operator documentation route."""

from flask import abort, render_template
from flask_smorest import Blueprint

from coreaoke.lib.branding import get_lockdown
from coreaoke.lib.current_app import get_site_name

docs_bp = Blueprint("docs", __name__)


@docs_bp.route("/docs")
def docs():
    """Render the operator documentation page."""
    if get_lockdown():
        abort(403)
    return render_template("docs.html", site_title=get_site_name())
