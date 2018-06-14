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

from typing import Union
from pathlib import Path

import jinja2

from synthtool import tmp


PathOrStr = Union[str, Path]


class Templates:
    def __init__(self, location: PathOrStr) -> None:
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(location)),
            autoescape=False)
        self.dir = tmp.tmpdir()

    def render(self, template_name: str, **kwargs) -> Path:
        template = self.env.get_template(template_name)

        output = template.render(**kwargs)

        dest = self.dir / template_name
        dest.write_text(output)

        return dest
