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
