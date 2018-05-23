import pathlib


def get_cache_dir() -> pathlib.Path:
    return pathlib.Path.home() / '.cache' / 'synthtool'
