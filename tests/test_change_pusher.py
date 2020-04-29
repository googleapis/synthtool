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

from autosynth.change_pusher import build_pr_body
from integration_tests import util


def test_build_pr_body_with_synth_log():
    synth_log = "The best pull request ever!"
    pr_body = build_pr_body(synth_log)
    assert pr_body.find(synth_log) > -1


def test_build_pr_body_with_kokoro_build_id():
    with util.ModifiedEnvironment({"KOKORO_BUILD_ID": "42"}):
        pr_body = build_pr_body("")
        assert (
            pr_body.find("https://source.cloud.google.com/results/invocations/42") > -1
        )


def test_build_pr_body_with_synth_log_and_kokoro_build_id():
    with util.ModifiedEnvironment({"KOKORO_BUILD_ID": "42"}):
        # The synth log should override the kokoro build id.
        synth_log = "A great pull request."
        pr_body = build_pr_body(synth_log)
        assert (
            pr_body.find("https://source.cloud.google.com/results/invocations/42") == -1
        )
        assert pr_body.find(synth_log) > -1
