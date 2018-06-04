"""Tracked paths.

This is a bit of a hack.
"""

import pathlib


_tracked_paths = []


def add(path):
    _tracked_paths.append(pathlib.Path(path))


def relativize(path):
    path = pathlib.Path(path)
    for tracked_path in _tracked_paths:
        try:
            return path.relative_to(tracked_path)
        except ValueError:
            pass
    raise ValueError(f'The root for {path} is not tracked.')
