from pathlib import Path
from typing import List


class GAPICGenerator:
    def py_library(self) -> Path:
        raise NotImplemented()


class CommonTemplates:
    def py_library(self) -> Path:
        raise NotImplemented()

    def render(self, rst_file, versions: List[str]) -> Path:
        '''
        example:
        render('python/docs/index.rst', versions=['v1', 'v1beta1']):
        '''
        raise NotImplemented()
