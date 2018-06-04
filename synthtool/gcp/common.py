from pathlib import Path

from synthtool.sources import templates


_TEMPLATES_DIR = Path(__file__).parent / 'templates'


class CommonTemplates:
    def __init__(self):
        self._templates = templates.Templates(_TEMPLATES_DIR)

    def py_library(self) -> Path:
        raise NotImplemented()

    def render(self, template_name: str, **kwargs) -> Path:
        return self._templates.render(template_name, **kwargs)
