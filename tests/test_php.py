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


from pathlib import Path

import pytest


FIXTURES = Path(__file__).parent / "fixtures" / "php"


@pytest.fixture(scope="function", params=["asset", "secret_manager"])
def prepare_test_data(request):
    """A fixture for preparing test data.
    """
    param = request.param
    print(f"Setup prepare_test_data with %s", param)
    yield param
    print(f"Teardown %s", param)


def test_owlbot_php(prepare_test_data):
    pass
