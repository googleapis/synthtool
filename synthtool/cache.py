import pathlib


def get_cache_dir() -> pathlib.Path:
    cache_dir = pathlib.Path.home() / '.cache' / 'synthtool'
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir
