from coraoke.karaoke import Karaoke
from coraoke.lib.get_platform import get_platform
from coraoke.version import __version__

PACKAGE = __package__
VERSION = __version__

__all__ = [
    "VERSION",
    "PACKAGE",
    Karaoke.__name__,
    get_platform.__name__,
]
