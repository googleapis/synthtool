import importlib
import os

import click

from synthtool import log


@click.command()
@click.version_option(message="%(version)s")
def main():
    synth_file = os.path.join(os.getcwd(), "synth.py")

    if os.path.lexists(synth_file):
        log.debug(f"Executing {synth_file}.")
        # https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly
        spec = importlib.util.spec_from_file_location("synth", synth_file)
        synth_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(synth_module)
    else:
        log.exception(f"{synth_file} not found.")
