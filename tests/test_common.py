# Copyright 2019 Google LLC
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

from synthtool.gcp.common import decamelize


def test_converts_camel_to_title():
    assert decamelize("fooBar") == "Foo Bar"
    assert decamelize("fooBarSnuh") == "Foo Bar Snuh"


def test_handles_acronym():
    assert decamelize("ACL") == "ACL"
    assert decamelize("coolACL") == "Cool ACL"


def test_handles_spaces():
    assert decamelize("cool api") == "Cool Api"
