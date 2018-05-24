import atexit
from pathlib import Path
import shutil
import tempfile
from typing import List

from synthtool import log


_tempdirs: List[str] = []


def tmpdir() -> Path:
    path = tempfile.mkdtemp()
    _tempdirs.append(path)
    return Path(path)


def cleanup():
    for path in _tempdirs:
        shutil.rmtree(str(path))
    log.debug(f'Cleaned up {len(_tempdirs)} temporary directories.')


atexit.register(cleanup)
