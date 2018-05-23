import pathlib
import shutil

from synthtool import cache
from synthtool import shell


def clone(
        url: str,
        dest: pathlib.Path = None,
        committish: str = 'master',
        force: bool = False) -> pathlib.Path:

    if dest is None:
        dest = cache.get_cache_dir()

    dest = dest / pathlib.Path(url).stem

    if force and dest.exists():
        shutil.rmtree(dest)

    if not dest.exists():
        shell.run([
            'git', 'clone', url, dest])
    else:
        shell.run([
            'git', 'pull'], cwd=str(dest))

    shell.run([
        'git', 'reset', '--hard', committish], cwd=str(dest))

    return dest
