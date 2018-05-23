import subprocess

from synthtool import log


def run(args, *, cwd=None, check=True):
    try:
        return subprocess.run(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            cwd=cwd,
            check=check,
            encoding='utf-8',
        )
    except subprocess.CalledProcessError as exc:
        log.error(f"Failed executing {' '.join(args)}:\n\n{exc.stdout}")
        raise exc
