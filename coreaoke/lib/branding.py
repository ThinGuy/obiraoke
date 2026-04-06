"""White-label branding configuration from snap environment variables."""

import os

_DEFAULT_APP_NAME = "Ubuntu Coreaoke"
_DEFAULT_ICON_URL = "/images/logo"


def get_branding() -> dict:
    """Return branding settings from environment variables.

    Keys:
        app_name: Display name from COREAOKE_APP_NAME env var.
        app_icon_url: URL path to serve the icon. Points to /branding/icon
            when COREAOKE_APP_ICON is set and the file exists, otherwise
            falls back to the built-in logo at /images/logo.
    """
    app_name = os.environ.get("COREAOKE_APP_NAME") or _DEFAULT_APP_NAME

    custom_icon_path = os.environ.get("COREAOKE_APP_ICON", "")
    if custom_icon_path and os.path.isfile(custom_icon_path):
        app_icon_url = "/branding/icon"
    else:
        app_icon_url = _DEFAULT_ICON_URL

    return {
        "app_name": app_name,
        "app_icon_url": app_icon_url,
    }
