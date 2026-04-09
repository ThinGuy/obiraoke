"""Software Bill of Materials route."""

import importlib.metadata

from flask import abort, jsonify, render_template, request
from flask_smorest import Blueprint

from coreaoke import VERSION
from coreaoke.lib.branding import get_lockdown
from coreaoke.lib.current_app import get_site_name

sbom_bp = Blueprint("sbom", __name__)

BUNDLED_COMPONENTS = [
    {"name": "FFmpeg", "version": "", "license": "LGPL-2.1"},
    {"name": "yt-dlp", "version": "", "license": "Unlicense"},
    {"name": "HLS.js", "version": "", "license": "Apache-2.0"},
    {"name": "Selectize.js", "version": "", "license": "Apache-2.0"},
    {"name": "Fontello", "version": "", "license": "MIT"},
    {"name": "Ubuntu Variable Font", "version": "", "license": "UFL-1.0"},
]


def _get_python_packages() -> list[dict[str, str]]:
    """Return installed Python packages sorted by name."""
    packages = []
    for dist in importlib.metadata.distributions():
        name = dist.metadata["Name"]
        version = dist.metadata["Version"]
        if name.lower() == "coreaoke":
            version = VERSION
        license_id = dist.metadata.get("License-Expression") or dist.metadata.get("License") or ""
        packages.append({"name": name, "version": version, "license": license_id})
    packages.sort(key=lambda p: p["name"].lower())
    return packages


@sbom_bp.route("/sbom")
def sbom():
    """Render or return the Software Bill of Materials."""
    if get_lockdown():
        abort(403)
    python_packages = _get_python_packages()

    if request.args.get("format") == "json":
        return jsonify(
            {
                "python_packages": python_packages,
                "bundled_components": BUNDLED_COMPONENTS,
            }
        )

    return render_template(
        "sbom.html",
        site_title=get_site_name(),
        python_packages=python_packages,
        bundled_components=BUNDLED_COMPONENTS,
    )
