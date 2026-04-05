"""Image serving routes for QR code and logo."""
import logging
import os

import flask_babel
from flask import send_file
from flask_smorest import Blueprint

from coreaoke.lib.current_app import get_karaoke_instance

_ = flask_babel.gettext
logger = logging.getLogger(__name__)

images_bp = Blueprint("images", __name__)

_BUILTIN_LOGO = os.path.normpath(
    os.path.join(os.path.dirname(__file__), "..", "static", "images", "logo.png")
)


@images_bp.route("/qrcode")
def qrcode():
    """Get QR code image for the web interface URL."""
    k = get_karaoke_instance()
    if not k.qr_code_path or not os.path.exists(k.qr_code_path):
        return '', 404
    return send_file(k.qr_code_path, mimetype="image/png")


@images_bp.route("/logo")
def logo():
    """Get the logo image, falling back to built-in static asset."""
    k = get_karaoke_instance()
    logo_path = os.path.abspath(k.logo_path)
    if not os.path.exists(logo_path):
        logger.warning("Configured logo_path does not exist: %s — falling back to built-in logo", logo_path)
        logo_path = _BUILTIN_LOGO
    return send_file(logo_path, mimetype="image/png")
