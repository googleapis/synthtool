# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pathlib import Path
import shutil
from typing import Callable, Iterable, Union
import os
import re
import sys

from synthtool import _tracked_paths
from synthtool import log

PathOrStr = Union[str, Path]
ListOfPathsOrStrs = Iterable[Union[str, Path]]


def _expand_paths(paths: ListOfPathsOrStrs, root: PathOrStr = None) -> Iterable[Path]:
    """Given a list of globs/paths, expands them into a flat sequence,
    expanding globs as necessary."""
    if paths is None:
        return []

    if isinstance(paths, (str, Path)):
        paths = [paths]

    if root is None:
        root = Path(".")

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
            yield from (
                p
                for p in root.glob(path)
                if p.absolute() != Path(synth_script_name).absolute()
            )


def _filter_files(paths: Iterable[Path]) -> Iterable[Path]:
    """Returns only the paths that are files (no directories)."""

    return (path for path in paths if path.is_file() and os.access(path, os.W_OK))


def _merge_file(
    source_path: Path, dest_path: Path, merge: Callable[[str, str, Path], str]
):
    """
    Writes to the destination the result of merging the source with the
    existing destination contents, using the given merge function.

    The merge function must take three arguments: the source contents, the
    old destination contents, and a Path to the file to be written.
    """

    with source_path.open("r") as source_file:
        source_text = source_file.read()

    with dest_path.open("r+") as dest_file:
        dest_text = dest_file.read()

        final_text = merge(source_text, dest_text, dest_path)

        if final_text != dest_text:
            dest_file.seek(0)
            dest_file.write(final_text)
            dest_file.truncate()


def _copy_dir_to_existing_dir(
    source: Path,
    destination: Path,
    excludes: ListOfPathsOrStrs = None,
    merge: Callable[[str, str, Path], str] = None,
) -> bool:
    """
    copies files over existing files to an existing directory
    this function does not copy empty directories.

    Returns: True if any files were copied, False otherwise.
    """
    copied = False

    if not excludes:
        excludes = []
    for root, _, files in os.walk(source):
        for name in files:
            rel_path = str(Path(root).relative_to(source))
            dest_dir = destination / rel_path
            dest_path = dest_dir / name
            exclude = [
                e
                for e in excludes
                if (
                    Path(e).relative_to(".") == Path(rel_path)
                    or Path(e).relative_to(".") == Path(rel_path) / name
                )
            ]
            if not exclude:
                os.makedirs(str(dest_dir), exist_ok=True)
                source_path = Path(os.path.join(root, name))
                if merge is not None and dest_path.is_file():
                    _merge_file(source_path, dest_path, merge)
                else:
                    shutil.copy2(str(source_path), str(dest_path))
                copied = True

    return copied


def move(
    sources: ListOfPathsOrStrs,
    destination: PathOrStr = None,
    excludes: ListOfPathsOrStrs = None,
    merge: Callable[[str, str, Path], str] = None,
) -> bool:
    """
    copy file(s) at source to current directory, preserving file mode.

    Returns: True if any files were copied, False otherwise.
    """
    copied = False

    for source in _expand_paths(sources):
        if destination is None:
            canonical_destination = _tracked_paths.relativize(source)
        else:
            canonical_destination = Path(destination)

        if excludes:
            excludes = [
                _tracked_paths.relativize(e) for e in _expand_paths(excludes, source)
            ]
        else:
            excludes = []
        if source.is_dir():
            copied = copied or _copy_dir_to_existing_dir(
                source, canonical_destination, excludes=excludes, merge=merge
            )
        elif source not in excludes:
            # copy individual file
            if merge is not None and canonical_destination.is_file():
                _merge_file(source, canonical_destination, merge)
            else:
                shutil.copy2(source, canonical_destination)
            copied = True

    if not copied:
        log.warning(
            f"No files in sources {sources} were copied. Does the source "
            f"contain files?"
        )

    return copied


def _replace_in_file(path, expr, replacement):
    with path.open("r+") as fh:
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
    sources: ListOfPathsOrStrs, before: str, after: str, flags: int = re.MULTILINE
):
    """Replaces occurrences of before with after in all the given sources."""
    expr = re.compile(before, flags=flags or 0)
    paths = _filter_files(_expand_paths(sources, "."))

    if not paths:
        log.warning(f"No files were found in sources {sources} for replace()")

    any_replaced = False
    for path in paths:
        replaced = _replace_in_file(path, expr, after)
        any_replaced = any_replaced or replaced
        if replaced:
            log.info(f"Replaced {before!r} in {path}.")

    if not any_replaced:
        log.warning(
            f"No replacements made in {sources} for pattern {before}, maybe "
            "replacement is not longer needed?"
        )
