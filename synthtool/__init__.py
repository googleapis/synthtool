"""Synthtool synthesizes libraries from disparate sources."""

from synthtool.transforms import move, replace

__version__ = '0.0.1'


copy = move

__all__ = [
    "copy",
    "move",
    "replace",
]
