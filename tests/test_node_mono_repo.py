# Copyright 2020 Google LLC
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

import filecmp
import pathlib
import re
from pathlib import Path
from unittest import TestCase
from unittest.mock import Mock, patch
from datetime import date

import pytest

from synthtool.languages import node_mono_repo
from . import util

FIXTURES = Path(__file__).parent / "fixtures"
TEMPLATES = Path(__file__).parent.parent / "synthtool" / "gcp" / "templates"


def test_quickstart_metadata_with_snippet():
    with util.chdir(FIXTURES / "node_templates" / "standard"):
        metadata = node_mono_repo.template_metadata(
            FIXTURES / "node_templates" / "standard"
        )

        # should have loaded the special quickstart sample (ignoring header).
        assert "ID of the Cloud Bigtable instance" in metadata["quickstart"]
        assert "limitations under the License" not in metadata["quickstart"]

        assert isinstance(metadata["samples"], list)

        # should have a link to the quickstart in the samples
        sample_names = list(map(lambda sample: sample["file"], metadata["samples"]))
        assert (
            len(
                list(filter((re.compile("samples/quickstart.js$")).match, sample_names))
            )
            == 0
        )


def test_package_json_mono_repo():
    with util.chdir(FIXTURES / "node_templates" / "package_json_mono_repo"):
        metadata = node_mono_repo.template_metadata(
            FIXTURES / "node_templates" / "package_json_mono_repo"
        )
        assert (
            "https://github.com/googleapis/google-cloud-node/tree/main/packages/google-cloud-dlp"
            in metadata["homepage"]
        )
        print(metadata["full_directory_path"])
        assert (
            "google-cloud-node/packages/google-cloud-dlp"
            in metadata["full_directory_path"]
        )


def test_metadata_engines_field():
    with util.chdir(FIXTURES / "node_templates" / "standard"):
        metadata = node_mono_repo.template_metadata(
            FIXTURES / "node_templates" / "standard"
        )
        assert "10" in metadata["engine"]


def test_quickstart_metadata_without_snippet():
    with util.chdir(FIXTURES / "node_templates" / "no_quickstart_snippet"):
        metadata = node_mono_repo.template_metadata(
            FIXTURES / "node_templates" / "no_quickstart_snippet"
        )

        # should not have populated the quickstart for the README
        assert not metadata["quickstart"]

        assert isinstance(metadata["samples"], list)

        # should not have a link to the quickstart in the samples
        sample_names = list(map(lambda sample: sample["file"], metadata["samples"]))
        assert "samples/quickstart.js" not in sample_names


def test_no_samples():
    # use a non-nodejs template directory
    with util.chdir(FIXTURES):
        metadata = node_mono_repo.template_metadata(FIXTURES)

        # should not have populated the quickstart for the README
        assert not metadata["quickstart"]

        assert isinstance(metadata["samples"], list)
        assert len(metadata["samples"]) == 0


def test_fix_sample_file_path():
    with util.copied_fixtures_dir(FIXTURES / "nodejs_mono_repo_with_samples"):
        metadata = node_mono_repo.template_metadata(
            FIXTURES / "nodejs_mono_repo_with_samples" / "packages" / "datastore"
        )

        print(metadata["samples"])

        assert metadata["samples"] == [
            {
                "title": "Compare_to_quickstart",
                "file": "packages/datastore/samples/generated/compare_to_quickstart.js",
            },
            {
                "title": "Dataproc_metastore.create_backup",
                "file": "packages/datastore/samples/generated/v1/dataproc_metastore.create_backup.js",
            },
            {
                "title": "Dataproc_metastore.list_backups",
                "file": "packages/datastore/samples/generated/v1/dataproc_metastore.list_backups.js",
            },
        ]


def test_extract_clients_no_file():
    index_ts_path = pathlib.Path(
        FIXTURES / "node_templates" / "index_samples" / "no_exist_index.ts"
    )

    with pytest.raises(FileNotFoundError):
        clients = node_mono_repo.extract_clients(index_ts_path)
        assert not clients


def test_extract_single_clients():
    index_ts_path = pathlib.Path(
        FIXTURES / "node_templates" / "index_samples" / "single_index.ts"
    )

    clients = node_mono_repo.extract_clients(index_ts_path)

    assert len(clients) == 1
    assert clients[0] == "TextToSpeechClient"


def test_extract_multiple_clients():
    index_ts_path = pathlib.Path(
        FIXTURES / "node_templates" / "index_samples" / "multiple_index.ts"
    )

    clients = node_mono_repo.extract_clients(index_ts_path)

    assert len(clients) == 2
    assert clients[0] == "StreamingVideoIntelligenceServiceClient"
    assert clients[1] == "VideoIntelligenceServiceClient"


def test_generate_index_ts():
    # use a non-nodejs template directory
    with util.chdir(FIXTURES / "node_templates" / "index_samples"):
        node_mono_repo.generate_index_ts(
            ["v1", "v1beta1"],
            "v1",
            relative_dir=(FIXTURES / "node_templates" / "index_samples"),
            year="2020",
        )
        generated_index_path = pathlib.Path(
            FIXTURES / "node_templates" / "index_samples" / "src" / "index.ts"
        )
        sample_index_path = pathlib.Path(
            FIXTURES / "node_templates" / "index_samples" / "sample_index.ts"
        )
        assert filecmp.cmp(generated_index_path, sample_index_path)


def test_generate_index_ts_esm():
    # use a non-nodejs template directory
    with util.chdir(FIXTURES / "node_templates" / "index_esm_samples"):
        node_mono_repo.generate_index_ts(
            ["v1", "v1beta1"],
            "v1",
            relative_dir=(FIXTURES / "node_templates" / "index_esm_samples"),
            year="2020",
            is_esm=True,
        )
        generated_index_path = pathlib.Path(
            FIXTURES
            / "node_templates"
            / "index_esm_samples"
            / "esm"
            / "src"
            / "index.ts"
        )
        sample_index_path = pathlib.Path(
            FIXTURES / "node_templates" / "index_esm_samples" / "sample_index.ts"
        )
        assert filecmp.cmp(generated_index_path, sample_index_path)


def test_write_release_please_config():
    # use a non-nodejs template directory
    with util.copied_fixtures_dir(FIXTURES / "node_templates" / "release_please"):
        node_mono_repo.write_release_please_config(
            [
                "google-cloud-node/packages/gapic-node-processing/templates/bootstrap-templates",
                "Users/person/google-cloud-node/packages/dlp",
                "Users/person/google-cloud-node/packages/asset",
                "packages/bigquery-migration",
            ]
        )

        assert filecmp.cmp(
            pathlib.Path("release-please-config.json"),
            pathlib.Path("release-please-config-post.json"),
        )


def test_generate_index_ts_empty_versions():
    # use a non-nodejs template directory
    with util.chdir(FIXTURES / "node_templates" / "index_samples"):
        with pytest.raises(AttributeError) as err:
            node_mono_repo.generate_index_ts(
                [],
                "v1",
                relative_dir=(FIXTURES / "node_templates" / "index_samples",),
                year=date.today().year,
            )
            assert "can't be empty" in err.args


def test_generate_esm_index_ts_empty_versions():
    # use a non-nodejs template directory
    with util.chdir(FIXTURES / "node_templates" / "index_esm_samples"):
        with pytest.raises(AttributeError) as err:
            node_mono_repo.generate_index_ts(
                [],
                "v1",
                relative_dir=(FIXTURES / "node_templates" / "index_esm_samples",),
                year=date.today().year,
                is_esm=True,
            )
            assert "can't be empty" in err.args


def test_generate_index_ts_invalid_default_version():
    # use a non-nodejs template directory
    with util.chdir(FIXTURES / "node_templates" / "index_samples"):
        versions = ["v1beta1"]
        default_version = "v1"

        with pytest.raises(AttributeError) as err:
            node_mono_repo.generate_index_ts(
                versions,
                default_version,
                relative_dir=(FIXTURES / "node_templates" / "index_samples"),
                year=date.today().year,
            )
            assert f"must contain default version {default_version}" in err.args


def test_generate_index_ts_no_clients():
    # use a non-nodejs template directory
    with util.chdir(FIXTURES / "node_templates" / "index_samples"):
        versions = ["v1", "v1beta1", "invalid_index"]
        default_version = "invalid_index"

        with pytest.raises(AttributeError) as err:
            node_mono_repo.generate_index_ts(
                versions,
                default_version,
                relative_dir=(FIXTURES / "node_templates" / "index_samples"),
                year=date.today().year,
            )
            assert (
                f"No client is exported in the default version's({default_version}) index.ts ."
                in err.args
            )


def test_generate_index_ts_no_clients_esm():
    # use a non-nodejs template directory
    with util.chdir(FIXTURES / "node_templates" / "index_esm_samples"):
        versions = ["v1", "v1beta1", "invalid_index"]
        default_version = "invalid_index"

        with pytest.raises(AttributeError) as err:
            node_mono_repo.generate_index_ts(
                versions,
                default_version,
                relative_dir=(FIXTURES / "node_templates" / "index_esm_samples"),
                year=date.today().year,
                is_esm=True,
            )
            assert (
                f"No client is exported in the default version's({default_version}) index.ts ."
                in err.args
            )


class TestPostprocess(TestCase):
    @patch("synthtool.shell.run")
    def test_install(self, shell_run_mock):
        node_mono_repo.install()
        calls = shell_run_mock.call_args_list
        assert any(["npm install" in " ".join(call[0][0]) for call in calls])

    @patch("synthtool.shell.run")
    def test_fix(self, shell_run_mock):
        node_mono_repo.fix()
        calls = shell_run_mock.call_args_list
        assert any(["npm run fix" in " ".join(call[0][0]) for call in calls])

    @patch("synthtool.shell.run")
    def test_compile_protos(self, shell_run_mock):
        node_mono_repo.compile_protos()
        calls = shell_run_mock.call_args_list
        assert any(["npx compileProtos src" in " ".join(call[0][0]) for call in calls])

    @patch("synthtool.shell.run")
    def test_compile_protos_esm(self, shell_run_mock):
        node_mono_repo.compile_protos(is_esm=True)
        calls = shell_run_mock.call_args_list
        assert any(
            [
                "npx compileProtos esm/src --esm" in " ".join(call[0][0])
                for call in calls
            ]
        )

    @patch("synthtool.shell.run")
    def test_compile_protos_hermetic(self, shell_run_mock):
        node_mono_repo.compile_protos_hermetic(relative_dir="any", is_esm=False)
        calls = shell_run_mock.call_args_list
        assert any(
            [
                "/node_modules/.bin/compileProtos src" in " ".join(call[0][0])
                for call in calls
            ]
        )

    @patch("synthtool.shell.run")
    def test_compile_protos_hermetic_esm(self, shell_run_mock):
        node_mono_repo.compile_protos_hermetic(relative_dir="any", is_esm=True)
        calls = shell_run_mock.call_args_list
        assert any(
            [
                "/node_modules/.bin/compileProtos esm/src --esm" in " ".join(call[0][0])
                for call in calls
            ]
        )

    @patch("synthtool.shell.run")
    def test_postprocess_gapic_library(self, shell_run_mock):
        node_mono_repo.postprocess_gapic_library()
        calls = shell_run_mock.call_args_list
        assert any(["npm install" in " ".join(call[0][0]) for call in calls])
        assert any(["npm run fix" in " ".join(call[0][0]) for call in calls])
        assert any(["npx compileProtos src" in " ".join(call[0][0]) for call in calls])

    @patch("synthtool.shell.run")
    def test_postprocess_gapic_library_esm(self, shell_run_mock):
        node_mono_repo.postprocess_gapic_library(is_esm=True)
        calls = shell_run_mock.call_args_list
        assert any(["npm install" in " ".join(call[0][0]) for call in calls])
        assert any(["npm run fix" in " ".join(call[0][0]) for call in calls])
        assert any(
            [
                "npx compileProtos esm/src --esm" in " ".join(call[0][0])
                for call in calls
            ]
        )


@pytest.fixture
def nodejs_mono_repo():
    """chdir to a copy of nodejs-dlp-with-staging."""
    with util.copied_fixtures_dir(
        FIXTURES / "nodejs_mono_repo_with_staging"
    ) as workdir:
        yield workdir


@pytest.fixture
def nodejs_mono_repo_esm():
    """chdir to a copy of nodejs_mono_repo_esm"""
    with util.copied_fixtures_dir(FIXTURES / "nodejs_mono_repo_esm") as workdir:
        yield workdir


@patch("subprocess.run")
def test_walk_through_owlbot_dirs_git_diff(mock_subproc_popen):
    process_mock = Mock()
    attrs = {"communicate.return_value": ("output", "error")}
    process_mock.configure_mock(**attrs)
    mock_subproc_popen.return_value = process_mock
    node_mono_repo.walk_through_owlbot_dirs(
        FIXTURES / "nodejs_mono_repo_with_staging", search_for_changed_files=True
    )
    assert mock_subproc_popen.called


@patch("subprocess.run")
def test_walk_through_owlbot_dirs(mock_subproc_popen):
    process_mock = Mock()
    attrs = {"communicate.return_value": ("output", "error")}
    process_mock.configure_mock(**attrs)
    mock_subproc_popen.return_value = process_mock
    owlbot_dirs = node_mono_repo.walk_through_owlbot_dirs(
        FIXTURES / "nodejs_mono_repo_with_staging", search_for_changed_files=False
    )
    assert not mock_subproc_popen.called
    assert re.search("packages/dlp", owlbot_dirs[0])


@patch("subprocess.run")
def test_walk_through_owlbot_dirs_handwritten(mock_subproc_popen):
    process_mock = Mock()
    attrs = {"communicate.return_value": ("output", "error")}
    process_mock.configure_mock(**attrs)
    mock_subproc_popen.return_value = process_mock

    with util.copied_fixtures_dir(
        FIXTURES / "nodejs_mono_repo_with_staging"
    ) as workdir:
        # Create a handwritten package
        handwritten_dir = workdir / "handwritten" / "my-package"
        handwritten_dir.mkdir(parents=True)
        (handwritten_dir / ".OwlBot.yaml").touch()

        owlbot_dirs = node_mono_repo.walk_through_owlbot_dirs(
            workdir, search_for_changed_files=False
        )

        assert not mock_subproc_popen.called
        assert len(owlbot_dirs) == 3

        handwritten_count = sum(
            1 for d in owlbot_dirs if re.search("handwritten/my-package", d)
        )
        assert handwritten_count == 1

        package_dlp_count = sum(1 for d in owlbot_dirs if re.search("packages/dlp", d))
        staging_dlp_count = sum(
            1 for d in owlbot_dirs if re.search("owl-bot-staging/dlp", d)
        )

        assert package_dlp_count + staging_dlp_count == 2


@patch("synthtool.languages.node_mono_repo.walk_through_owlbot_dirs")
def test_entrypoint_args_with_no_arg(hermetic_mock, nodejs_mono_repo):
    node_mono_repo.owlbot_entrypoint()
    node_mono_repo.walk_through_owlbot_dirs.assert_called_with(
        Path.cwd(), search_for_changed_files=True
    )
