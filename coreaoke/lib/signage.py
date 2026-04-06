"""Directory-based digital signage channel system."""

import logging
import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

_VIDEO_EXTENSIONS = {".mp4"}
_SOUND_EXTENSIONS = {".mp3"}
_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}

_DEFAULT_CONFIG = {
    "name": "",
    "layout": "lobby",
    "bg_video_interval": 30,
    "bg_sound_volume": 0.3,
    "show_qr": True,
    "show_logo": True,
    "show_clock": False,
}


@dataclass
class QrEntry:
    label: str
    url: str


@dataclass
class SignageChannel:
    """A single signage channel loaded from a directory."""

    name: str
    layout: str
    bg_videos: list[str] = field(default_factory=list)
    bg_sounds: list[str] = field(default_factory=list)
    logo_path: str | None = None
    qr_entries: list[QrEntry] = field(default_factory=list)
    config: dict = field(default_factory=dict)


def get_signage_root() -> Path:
    """Return the signage root directory, respecting $SNAP_COMMON."""
    if os.environ.get("SNAP"):
        base = os.environ.get("SNAP_COMMON", "/var/snap/coreaoke/common")
        return Path(base) / "signage"
    return Path.home() / ".local" / "share" / "coreaoke" / "signage"


def _sorted_files_by_ext(directory: Path, extensions: set[str]) -> list[str]:
    """Return filenames in directory matching extensions, sorted by name."""
    if not directory.is_dir():
        return []
    return sorted(
        f.name
        for f in directory.iterdir()
        if f.is_file() and f.suffix.lower() in extensions
    )


def _load_qr_entries(qr_dir: Path) -> list[QrEntry]:
    """Load QR entries from txt files in the qr/ subdirectory."""
    if not qr_dir.is_dir():
        return []
    entries = []
    for txt_file in sorted(qr_dir.iterdir()):
        if not txt_file.is_file() or txt_file.suffix.lower() != ".txt":
            continue
        url = txt_file.read_text().strip()
        if url:
            entries.append(QrEntry(label=txt_file.stem, url=url))
    return entries


def _find_first_image(directory: Path) -> str | None:
    """Return the filename of the first image in directory, or None."""
    files = _sorted_files_by_ext(directory, _IMAGE_EXTENSIONS)
    return files[0] if files else None


def load_channel(channel_name: str) -> SignageChannel | None:
    """Load a signage channel by directory name. Returns None if not found."""
    channel_dir = get_signage_root() / channel_name
    config_path = channel_dir / "channel.yaml"
    if not config_path.is_file():
        return None

    try:
        raw = yaml.safe_load(config_path.read_text()) or {}
    except yaml.YAMLError:
        logger.error("Invalid channel.yaml in %s", channel_dir)
        return None

    config = {**_DEFAULT_CONFIG, **raw}
    if not config["name"]:
        config["name"] = channel_name.replace("_", " ").replace("-", " ").title()

    logo_filename = _find_first_image(channel_dir / "logo")
    logo_path = f"logo/{logo_filename}" if logo_filename else None

    return SignageChannel(
        name=config["name"],
        layout=config["layout"],
        bg_videos=_sorted_files_by_ext(channel_dir / "bg-video", _VIDEO_EXTENSIONS),
        bg_sounds=_sorted_files_by_ext(channel_dir / "bg-sound", _SOUND_EXTENSIONS),
        logo_path=logo_path,
        qr_entries=_load_qr_entries(channel_dir / "qr"),
        config=config,
    )


def list_channels() -> list[str]:
    """Return names of all valid signage channels (directories with channel.yaml)."""
    root = get_signage_root()
    if not root.is_dir():
        return []
    return sorted(
        d.name
        for d in root.iterdir()
        if d.is_dir() and (d / "channel.yaml").is_file()
    )
