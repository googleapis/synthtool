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
from importlib.abc import Loader
import importlib.util
import logging
import os
from pathlib import Path
import re
import typing

import synthtool as s
from synthtool.log import logger


STAGING_DIR = "owl-bot-staging"
METADATA_DIR = "GPBMetadata"
COPYRIGHT_REGEX = re.compile(r"Copyright (\d{4}) Google LLC$", flags=re.MULTILINE)
OWLBOT_PY_FILENAME = "owlbot.py"


# A dictionary containing dymanically loaded owlbot.py modules.
# The key is the destination path.
owlbot_py_cache: typing.Dict[str, typing.Any] = {}


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


def get_owlbot_py(dest: str) -> typing.Any:
    """Dynamically load owlbot.py and returns it as a loaded module.
    """
    global owlbot_py_cache
    if dest in owlbot_py_cache:
        return owlbot_py_cache[dest]
    owlbot_py = dest / OWLBOT_PY_FILENAME
    if owlbot_py.is_file():
        logger.debug("loading %s", owlbot_py)
        spec = importlib.util.spec_from_file_location("owlbot.py", owlbot_py)
        owlbot_py_cache[dest] = importlib.util.module_from_spec(spec)
        if not isinstance(spec.loader, Loader):
            return None
        spec.loader.exec_module(owlbot_py_cache[dest])
        logger.debug("loaded %s", owlbot_py)
        return owlbot_py_cache[dest]


def owlbot_copy_version(src: Path, dest: Path) -> None:
    """Copies files from a version subdirectory.
    """
    logger.debug("owlbot_copy_version called from %s to %s", src, dest)

    # detect the version string for later use
    entries = os.scandir(src / "src")
    if not entries:
        logger.info("there is no src directory to copy")
        return
    version_string = os.path.basename(os.path.basename(next(entries)))
    logger.debug("version_string detected: %s", version_string)

    # copy all src including partial veneer classes
    s.move([src / "src"], dest / "src", merge=_merge)

    # copy tests
    s.move([src / "tests"], dest / "tests", merge=_merge)

    # detect the directory containing proto generated PHP source and metadata.
    entries = os.scandir(src / "proto/src")
    proto_dir = None
    metadata_dir = None
    if not entries:
        logger.info("there is no proto generated src directory to copy")
        return
    for entry in entries:
        if os.path.basename(entry.path) == METADATA_DIR:
            metadata_dir = _find_copy_target(Path(entry.path).resolve(), version_string)
        else:
            proto_dir = _find_copy_target(Path(entry.path).resolve(), version_string)

    # copy proto files
    if isinstance(proto_dir, Path):
        logger.debug("proto_dir detected: %s", proto_dir)
        s.move([proto_dir], dest / "src", merge=_merge)

    # copy metadata files
    if isinstance(metadata_dir, Path):
        logger.debug("metadata_dir detected: %s", metadata_dir)
        s.move([metadata_dir], dest / "metadata", merge=_merge)


def owlbot_common_patch() -> None:
    """Apply common replacements.

    Currently nothing here.
    """
    pass


def owlbot_patch(dest: Path) -> None:
    """Apply some replacements for copied libraries.
    """
    logger.debug("owlbot_patch called for %s", dest)

    with pushd(dest):
        # Apply common replacements.
        owlbot_common_patch()

        # Load owlbot.py and execute `patch` function if defined.
        owlbot_py = get_owlbot_py(dest)
        if owlbot_py and hasattr(owlbot_py, "patch"):
            owlbot_py.patch()


def owlbot_copy(src: Path, dest: Path) -> None:
    """Copies files from generated tree.
    """
    entries = os.scandir(src)
    if not entries:
        logger.info("there is no version subdirectory to copy")
        return
    for entry in entries:
        if entry.is_dir():
            version_src = Path(entry.path).resolve()
            owlbot_copy_version(version_src, dest)
    owlbot_patch(dest)


def owlbot_main() -> None:
    """Copies files from staging and template directories into current working dir.

    """
    logging.basicConfig(level=logging.INFO)

    logger.debug("owlbot_main called")

    staging = Path(STAGING_DIR)
    if staging.is_dir():
        logger.debug("Found the staging dir!")
        entries = os.scandir(staging)
        for entry in entries:
            if entry.is_dir():
                src = Path(entry.path).resolve()
                dest = Path(src.parts[-1]).resolve()
                if dest.is_dir():
                    owlbot_py = get_owlbot_py(dest)
                    if owlbot_py and hasattr(owlbot_py, "main"):
                        # owlbot.py has `main` method defined.
                        # Change directory and run `main`.
                        with pushd(dest):
                            owlbot_py.main(src)
                        continue
                else:
                    logger.info("destination %s not found, but continuing")
                owlbot_copy(src, dest)
    else:
        logger.debug("Staging dir not found.")


if __name__ == "__main__":
    owlbot_main()
