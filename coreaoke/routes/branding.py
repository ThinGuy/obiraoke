"""White-label branding routes for custom icon serving."""

import logging
import mimetypes
import os

from flask import send_file
from flask_smorest import Blueprint

logger = logging.getLogger(__name__)

branding_bp = Blueprint("branding", __name__)


@branding_bp.route("/branding/icon")
def icon():
    """Serve the custom branding icon file if set and exists, else the default logo."""
    custom_icon_path = os.environ.get("COREAOKE_APP_ICON", "")
    if custom_icon_path and os.path.isfile(custom_icon_path):
        mimetype = mimetypes.guess_type(custom_icon_path)[0] or "image/png"
        return send_file(custom_icon_path, mimetype=mimetype)

    # Fall back to the built-in logo
    builtin_logo = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "static", "images", "logo.png")
    )
    return send_file(builtin_logo, mimetype="image/png")
