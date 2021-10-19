# Copyright 2021 Google LLC
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


import contextlib
import logging
import os
from pathlib import Path
import re
import subprocess
import typing

import synthtool as s
from synthtool.log import logger


STAGING_DIR = "owl-bot-staging"
METADATA_DIR = "GPBMetadata"
COPYRIGHT_REGEX = re.compile(r"Copyright (\d{4}) Google LLC$", flags=re.MULTILINE)
OWLBOT_PY_FILENAME = "owlbot.py"
DEFAULT_COPY_EXCLUDES: typing.List[str] = []


@contextlib.contextmanager
def pushd(d: Path):
    """Create a context for changing directory.

    When exiting the context, it will go back to the original directory.
    """
    original_dir = os.getcwd()
    os.chdir(d)
    try:
        yield
    finally:
        os.chdir(original_dir)


def _merge(src: str, dest: str, path: Path):
    """Merge function for the PHP post processor.
    This should be used for most merges of newly generated and existing files.
    It preserves copyright year from destination files
    Args:
        src: Source file content from gapic
        dest: Destination file content
        path: Destination file path
    Returns:
        The merged file content.
    """
    logger.debug("_merge called for %s", path)
    m = re.search(COPYRIGHT_REGEX, dest)
    if m:
        return re.sub(COPYRIGHT_REGEX, f"Copyright {m.group(1)} Google LLC", src, 1)
    return src


def _find_copy_target(src: Path, version_string: str) -> typing.Optional[Path]:
    """Returns a directory contains the version subdirectory.
    """
    logger.debug("_find_copy_target called with %s and %s", src, version_string)
    entries = os.scandir(src)
    if not entries:
        return None
    for entry in entries:
        if entry.path.endswith(version_string):
            return src
        if entry.is_dir():
            return _find_copy_target(Path(entry.path).resolve(), version_string)
    return None


def owlbot_copy_version(
    src: Path, dest: Path, copy_excludes: typing.Optional[typing.List[str]] = None,
) -> None:
    """Copies files from a version subdirectory.
    """
    logger.debug("owlbot_copy_version called from %s to %s", src, dest)

    if copy_excludes is None:
        copy_excludes = DEFAULT_COPY_EXCLUDES
    # detect the version string for later use
    entries = os.scandir(src / "src")
    if not entries:
        logger.info("there is no src directory to copy")
        return
    version_string = os.path.basename(os.path.basename(next(entries)))
    logger.debug("version_string detected: %s", version_string)

    # copy all src including partial veneer classes
    s.move([src / "src"], dest / "src", merge=_merge, excludes=copy_excludes)

    # copy tests
    s.move([src / "tests"], dest / "tests", merge=_merge, excludes=copy_excludes)

    # detect the directory containing proto generated PHP source and metadata.
    proto_src = src / "proto/src"
    entries = os.scandir(proto_src)
    proto_dir = None
    metadata_dir = None
    if not entries:
        logger.info("there is no proto generated src directory to copy: %s", proto_src)
        return
    for entry in entries:
        if os.path.basename(entry.path) == METADATA_DIR:
            metadata_dir = _find_copy_target(Path(entry.path).resolve(), version_string)
        else:
            proto_dir = _find_copy_target(Path(entry.path).resolve(), version_string)

    # copy proto files
    if isinstance(proto_dir, Path):
        logger.debug("proto_dir detected: %s", proto_dir)
        s.move([proto_dir], dest / "src", merge=_merge, excludes=copy_excludes)

    # copy metadata files
    if isinstance(metadata_dir, Path):
        logger.debug("metadata_dir detected: %s", metadata_dir)
        s.move([metadata_dir], dest / "metadata", merge=_merge, excludes=copy_excludes)


def owlbot_patch() -> None:
    """Apply some replacements for copied libraries.

    This function assumes the current directory is the target.
    """
    logger.debug("owlbot_patch called for %s", os.getcwd())

    # Apply common replacements, currently nothing.
    pass


def owlbot_main(
    src: Path,
    dest: Path,
    copy_excludes: typing.Optional[typing.List[str]] = None,
    patch_func: typing.Callable[[], None] = owlbot_patch,
) -> None:
    """Copies files from generated tree.
    """
    entries = os.scandir(src)
    if not entries:
        logger.info("there is no version subdirectory to copy")
        return
    for entry in entries:
        if entry.is_dir():
            version_src = Path(entry.path).resolve()
            owlbot_copy_version(version_src, dest, copy_excludes)
    with pushd(dest):
        patch_func()


def owlbot_entrypoint(staging_dir: str = STAGING_DIR) -> None:
    """Copies files from staging and template directories into current working dir.

    """
    logging.basicConfig(level=logging.INFO)

    logger.debug("owlbot_main called")

    staging = Path(staging_dir)
    if staging.is_dir():
        logger.debug("Found the staging dir!")
        entries = os.scandir(staging)
        for entry in entries:
            if entry.is_dir():
                # We use the same directory name for destination.
                src = Path(entry.path).resolve()
                dest = Path(src.parts[-1]).resolve()
                owlbot_py = dest / OWLBOT_PY_FILENAME
                if owlbot_py.is_file():
                    subprocess.run(["python", owlbot_py], cwd=dest, check=True)
                else:
                    owlbot_main(src, dest)
    else:
        logger.debug("Staging dir not found.")


if __name__ == "__main__":
    owlbot_entrypoint()
