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

import json
import os
import pytest
import sys
import time

from synthtool import metadata
from synthtool.tmp import tmpdir


def test_add_git_source():
    metadata.reset()

    metadata.add_git_source(sha="sha", name="name", remote="remote")

    current = metadata.get()

    assert current.sources[0].git.sha == "sha"
    assert current.sources[0].git.name == "name"
    assert current.sources[0].git.remote == "remote"


def test_add_generator_source():
    metadata.reset()

    metadata.add_generator_source(name="name", version="1.2.3")

    current = metadata.get()

    assert current.sources[0].generator.name == "name"
    assert current.sources[0].generator.version == "1.2.3"


def test_add_template_source():
    metadata.reset()

    metadata.add_template_source(name="name", version="1.2.3")

    current = metadata.get()

    assert current.sources[0].template.name == "name"
    assert current.sources[0].template.version == "1.2.3"


def add_sample_client_destination():
    metadata.add_client_destination(
        source="source",
        api_name="api",
        api_version="v1",
        language="py",
        generator="gen",
        config="config",
    )


def test_add_client_destination():
    metadata.reset()

    add_sample_client_destination()

    current = metadata.get()

    assert current.destinations[0].client.source == "source"
    assert current.destinations[0].client.api_name == "api"
    assert current.destinations[0].client.api_version == "v1"
    assert current.destinations[0].client.language == "py"
    assert current.destinations[0].client.generator == "gen"
    assert current.destinations[0].client.config == "config"


def test_write(tmpdir):
    metadata.reset()

    metadata.add_git_source(sha="sha", name="name", remote="remote")

    output_file = tmpdir / "synth.metadata"

    metadata.write(str(output_file))

    raw = output_file.read()

    # Ensure the file was written, that *some* metadata is in it, and that it
    # is valid JSON.
    assert raw
    assert "sha" in raw
    data = json.loads(raw)
    assert data
    assert data["updateTime"] is not None


class SourceTree:
    """Creates a sample nested source file structure with known timestamps."""

    def __init__(self):
        self.tmpdir = tmpdir()
        # Create some files in nested directories:
        # src/a
        # src/code/b
        # src/code/c
        self.srcdir = self.tmpdir / "src"
        os.mkdir(self.srcdir)
        self.codedir = self.srcdir / "code"
        os.mkdir(self.codedir)
        with open(self.srcdir / "a", "wt") as file:
            file.write("a")
        # File systems timestamps have resolutions of about 1 second, so some
        # sleeping is necessary.
        time.sleep(1)
        self.after_a_before_b = time.time()
        time.sleep(1)
        self.b_path = os.path.join(self.codedir, "b")
        with open(self.b_path, "wt") as file:
            file.write("b")
        time.sleep(1)
        self.after_b_before_c = time.time()
        time.sleep(1)
        self.c_path = os.path.join(self.codedir, "c")
        with open(self.c_path, "wt") as file:
            file.write("c")


@pytest.fixture()
def source_tree_fixture():
    return SourceTree()


def test_new_files_found(source_tree_fixture):
    metadata.reset()

    # Confirm add_new_files found the new files and ignored the old one.
    metadata.add_new_files(
        source_tree_fixture.after_a_before_b, source_tree_fixture.srcdir
    )
    assert 2 == len(metadata.get().new_files)
    new_file_paths = [new_file.path for new_file in metadata.get().new_files]
    assert os.path.relpath(source_tree_fixture.b_path) in new_file_paths
    assert os.path.relpath(source_tree_fixture.c_path) in new_file_paths


def test_old_file_removed(source_tree_fixture):
    # Capture the list of files as old metadata.
    metadata.add_new_files(
        source_tree_fixture.after_a_before_b, source_tree_fixture.srcdir
    )

    # Prepare fresh metadata, with c as a new file and b as an obsolete file.
    old_metadata = metadata.get()
    metadata.reset()
    metadata.add_new_files(
        source_tree_fixture.after_b_before_c, source_tree_fixture.srcdir
    )
    assert 1 == len(metadata.get().new_files)
    assert (
        os.path.relpath(source_tree_fixture.c_path) == metadata.get().new_files[0].path
    )
    # Confirm remove_obsolete_files deletes b but not c.
    metadata.remove_obsolete_files(old_metadata)
    assert not os.path.exists(source_tree_fixture.b_path)
    assert os.path.exists(source_tree_fixture.c_path)

    # Confirm attempting to delete b a second time doesn't throw an exception.
    metadata.remove_obsolete_files(old_metadata)


def test_add_new_files_with_bad_file(tmpdir):
    metadata.reset()
    start_time = time.time()
    time.sleep(1)  # File systems have resolution of about 1 second.
    try:
        os.symlink(tmpdir / "does-not-exist", tmpdir / "badlink")
    except OSError:
        # On Windows, creating a symlink requires Admin priveleges, which
        # should never be granted to test runners.
        assert "win32" == sys.platform
        return
    # Confirm this doesn't throw an exception.
    metadata.add_new_files(start_time, tmpdir)
    # And a bad link does not exist and shouldn't be recorded as a new file.
    assert 0 == len(metadata.get().new_files)


def test_read_metadata(tmpdir):
    metadata.reset()
    add_sample_client_destination()
    metadata.write(tmpdir / "synth.metadata")
    read_metadata = metadata.read_or_empty(tmpdir / "synth.metadata")
    assert metadata.get() == read_metadata


def test_read_nonexistent_metadata(tmpdir):
    # The file doesn't exist.
    read_metadata = metadata.read_or_empty(tmpdir / "synth.metadata")
    metadata.reset()
    assert metadata.get() == read_metadata


@pytest.fixture(scope="function")
def preserve_track_obsolete_file_flag():
    should_track_obselete_files = metadata.should_track_obsolete_files()
    yield should_track_obselete_files
    metadata.set_track_obsolete_files(should_track_obselete_files)


def test_track_obsolete_files_defaults_to_true(preserve_track_obsolete_file_flag):
    assert metadata.should_track_obsolete_files()


def test_set_track_obsolete_files(preserve_track_obsolete_file_flag):
    metadata.set_track_obsolete_files(False)
    assert not metadata.should_track_obsolete_files()
    metadata.set_track_obsolete_files(True)
    assert metadata.should_track_obsolete_files()
