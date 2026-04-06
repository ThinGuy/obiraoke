"""Signage asset serving and QR code generation routes."""

import io
import logging
import mimetypes

import qrcode
from flask import abort, request, send_file
from flask_smorest import Blueprint
from qrcode.image.pure import PyPNGImage

from coreaoke.lib.signage import get_signage_root

logger = logging.getLogger(__name__)

signage_bp = Blueprint("signage", __name__)


@signage_bp.route("/signage/qr")
def signage_qr():
    """Generate and return a QR code PNG for the given URL."""
    url = request.args.get("url")
    if not url:
        abort(400)
    qr = qrcode.QRCode(version=1, box_size=4, border=4)
    qr.add_data(url)
    qr.make()
    img = qr.make_image(image_factory=PyPNGImage)
    buf = io.BytesIO()
    img.save(buf)
    buf.seek(0)
    return send_file(buf, mimetype="image/png")


@signage_bp.route("/signage/assets/<channel>/<subdir>/<filename>")
def signage_asset(channel: str, subdir: str, filename: str):
    """Serve a file from the signage directory with appropriate Content-Type."""
    # Prevent path traversal
    for part in (channel, subdir, filename):
        if ".." in part or "/" in part or "\\" in part:
            abort(400)

    file_path = get_signage_root() / channel / subdir / filename
    if not file_path.is_file():
        abort(404)

    # Resolve to ensure no symlink escape
    resolved = file_path.resolve()
    signage_resolved = get_signage_root().resolve()
    if not str(resolved).startswith(str(signage_resolved)):
        abort(403)

    mime_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    return send_file(resolved, mimetype=mime_type)
