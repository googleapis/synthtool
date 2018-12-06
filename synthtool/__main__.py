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

import importlib
import os
import sys
from typing import List, Sequence

import click
import pkg_resources

import synthtool.log
import synthtool.metadata


try:
    VERSION = pkg_resources.get_distribution("gcp-synthtool").version
except pkg_resources.DistributionNotFound:
    VERSION = "0.0.0+dev"


_extra_args: List[str] = []


def extra_args() -> List[str]:
    """Return any additional arguments specified to synthtool."""
    # Return a copy so these don't get modified.
    # A little trickery. If __name__ isn't __main__, import __main__ and return
    # its extra_args(). This ensures that both `from __main__ import extra_args()`
    # and `from synthtool.__main__ import extra_args()` works as expected. This
    # is needed because *technically* Python can have two copies of this module
    # in sys.modules when it's executed as main. Weird, I know.
    if __name__ != "__main__":  # pragma: no cover
        try:
            import __main__

            return __main__.extra_args()
        except AttributeError:
            # __main__ didn't have an extra_args() attribute, so this means
            # synthtool is not the main module. Just return what's in this
            # module.
            pass

    return list(_extra_args)


@click.command()
@click.version_option(message="%(version)s", version=VERSION)
@click.argument("synthfile", default="synth.py")
@click.option("--metadata", default="synth.metadata")
@click.argument("extra_args", nargs=-1)
def main(synthfile: str, metadata: str, extra_args: Sequence[str]):
    _extra_args.extend(extra_args)

    synthtool.metadata.register_exit_hook(outfile=metadata)

    synth_file = os.path.abspath(synthfile)

    if os.path.lexists(synth_file):
        synthtool.log.debug(f"Executing {synth_file}.")
        # https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly
        spec = importlib.util.spec_from_file_location("synth", synth_file)
        synth_module = importlib.util.module_from_spec(spec)

        if spec.loader is None:
            raise ImportError("Could not import synth.py")

        spec.loader.exec_module(synth_module)

    else:
        synthtool.log.exception(f"{synth_file} not found.")
        sys.exit(1)


if __name__ == "__main__":
    main()
