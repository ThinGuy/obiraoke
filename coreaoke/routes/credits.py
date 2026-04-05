"""Credits page route."""

from flask import render_template
from flask_smorest import Blueprint

from coreaoke.lib.current_app import get_site_name

credits_bp = Blueprint("credits", __name__)


@credits_bp.route("/credits")
def credits():
    """Render the credits and acknowledgements page."""
    return render_template(
        "credits.html",
        site_title=get_site_name(),
    )
