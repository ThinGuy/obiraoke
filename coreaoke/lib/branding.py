"""White-label branding configuration from snap environment variables."""

import os

_DEFAULT_APP_NAME = "Ubuntu Coreaoke"
_DEFAULT_ICON_URL = "/static/images/logo.png"


def get_branding() -> dict:
    """Return branding settings from environment variables.

    Keys:
        app_name: Display name from COREAOKE_APP_NAME env var.
        app_icon_url: URL path to serve the icon. Points to /branding/icon
            when COREAOKE_APP_ICON is set and the file exists, otherwise
            falls back to the built-in OB-01 image at /static/images/logo.png.
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


_VALID_LOGO_POSITIONS = {
    "top-left",
    "top-right",
    "bottom-left",
    "bottom-right",
    "center",
    "top-center",
    "bottom-center",
}


def get_logo_position() -> str:
    """Return the logo position from COREAOKE_LOGO_POSITION env var."""
    value = os.environ.get("COREAOKE_LOGO_POSITION", "center").strip().lower()
    if value in _VALID_LOGO_POSITIONS:
        return value
    return "center"


def get_lockdown() -> bool:
    """Return True when lockdown mode is enabled via COREAOKE_LOCKDOWN env var."""
    return os.environ.get("COREAOKE_LOCKDOWN", "").lower() == "true"
