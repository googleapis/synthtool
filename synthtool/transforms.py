from pathlib import Path
import shutil
from typing import Iterable, Union
import os
import re
import sys

from synthtool import _tracked_paths
from synthtool import log

PathOrStr = Union[str, Path]
ListOfPathsOrStrs = Iterable[Union[str, Path]]


def _expand_paths(
        paths: ListOfPathsOrStrs, root: PathOrStr = None) -> Iterable[Path]:
    """Given a list of globs/paths, expands them into a flat sequence,
    expanding globs as necessary."""
    if isinstance(paths, (str, Path)):
        paths = [paths]

    if root is None:
        root = Path('.')

    # ensure root is a path
    root = Path(root)

    # record name of synth script so we don't try to do transforms on it
    synth_script_name = sys.argv[0]

    for path in paths:
        if isinstance(path, Path):
            if path.is_absolute():
                anchor = Path(path.anchor)
                remainder = str(path.relative_to(path.anchor))
                yield from anchor.glob(remainder)
            else:
                yield path
        else:
            yield from (p for p in root.glob(path) if p != synth_script_name)


def _filter_files(paths: Iterable[Path]) -> Iterable[Path]:
    """Returns only the paths that are files (no directories)."""
    return (path for path in paths if path.is_file())


def _copy_dir_to_existing_dir(source: Path, destination: Path):
    """
    copies files over existing files to an existing directory
    this function does not copy empty directories
    """
    for root, _, files in os.walk(source):
        for name in files:
            rel_path = str(Path(root).relative_to(source)).lstrip('.')
            dest_dir = os.path.join(str(destination), rel_path)
            os.makedirs(dest_dir, exist_ok=True)
            dest_path = os.path.join(dest_dir, name)
            shutil.copyfile(os.path.join(root, name), dest_path)


def move(sources: ListOfPathsOrStrs, destination: PathOrStr = None):
    """
    copy file(s) at source to current directory
    """
    for source in _expand_paths(sources):
        if destination is None:
            canonical_destination = _tracked_paths.relativize(source)
        else:
            canonical_destination = Path(destination)

        if source.is_dir():
            _copy_dir_to_existing_dir(source, canonical_destination)
        else:
            # copy individual file
            shutil.copy2(source, canonical_destination)


def _replace_in_file(path, expr, replacement):
    with path.open('r+') as fh:
        content = fh.read()
        content, count = expr.subn(replacement, content)

        # Don't bother writing the file if we didn't change
        # anything.
        if not count:
            return False

        fh.seek(0)
        fh.write(content)
        fh.truncate()

    return True


def replace(
        sources: ListOfPathsOrStrs,
        before: str,
        after: str,
        flags: int = re.MULTILINE):
    """Replaces occurrences of before with after in all the given sources."""
    expr = re.compile(before, flags=flags or 0)
    paths = _filter_files(_expand_paths(sources, '.'))

    for path in paths:
        replaced = _replace_in_file(path, expr, after)
        if replaced:
            log.info(f"Replaced {before!r} in {path}.")
