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


from filecmp import dircmp
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

import pytest


FIXTURES = Path(__file__).parent / "fixtures" / "php"


@pytest.fixture(scope="session")
def docker_image():
    image_name = "owlbot-php-test"
    f = open("post-processor-changes.txt", "w")
    f.close()

    subprocess.run(
        [
            "docker",
            "build",
            "-t",
            image_name,
            "-f",
            "docker/owlbot/php/Dockerfile",
            ".",
        ],
        check=True,
    )
    yield image_name

    os.remove("post-processor-changes.txt")


@pytest.fixture(scope="session")
def hybrid_tmp_path():
    """A tmp dir implementation both for local run and on Kokoro.
    """
    # Trampoline mount KOKORO_ROOT at the same path.
    # So we can mount files under there with docker in docker.
    hybrid_dir = os.environ.get("KOKORO_ROOT", None)
    d = tempfile.mkdtemp(prefix="synthtool-php-test", dir=hybrid_dir)

    yield d

    shutil.rmtree(d)


@pytest.fixture(scope="function", params=["php_asset"])
def copy_fixture(request, hybrid_tmp_path):
    """A fixture for preparing test data.
    """
    param = request.param
    test_dir = Path(f"{hybrid_tmp_path}/{param}")

    shutil.copytree(FIXTURES / param, test_dir)
    print(f"Copied fixture to {test_dir}")

    yield test_dir

    shutil.rmtree(test_dir)


def get_diff_string(dcmp, buf=""):
    for name in dcmp.diff_files:
        buf += f"diff_file: {name} found in {dcmp.left} and {dcmp.right}\n"
    for sub_dcmp in dcmp.subdirs.values():
        buf += get_diff_string(sub_dcmp)
    return buf


def test_owlbot_php(copy_fixture, docker_image):
    user_id = os.getuid()
    group_id = os.getgid()
    src_dir = (copy_fixture / "src").resolve()

    # Run the postprocessor image
    subprocess.run(
        [
            "docker",
            "run",
            "--user",
            f"{user_id}:{group_id}",
            "--rm",
            "-v",
            f"{src_dir}:/repo",
            "-w",
            "/repo",
            docker_image,
        ],
        check=True,
    )

    dcmp = dircmp(copy_fixture / "expected", copy_fixture / "src")
    diff_string = get_diff_string(dcmp, "")
    assert diff_string == ""
    staging = copy_fixture / "src/owl-bot-staging"
    # make sure the staging directory is deleted
    assert not staging.is_dir()
