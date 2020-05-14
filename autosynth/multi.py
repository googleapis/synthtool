#!/usr/bin/env python3.6

"""Synthesizes multiple libraries and reports status."""

import argparse
import functools
import importlib
import os
import requests
import subprocess
import sys
import typing

import jinja2
import yaml

from autosynth import executor, github, synth
from autosynth.log import logger


def synthesize_library(
    library: typing.Dict, github_token: str, extra_args: typing.List[str]
) -> typing.Dict:
    """Run autosynth on a single library.

    Arguments:
        library {dict} - Library configuration

    """
    logger.info(f"Synthesizing {library['name']}.")

    command = [sys.executable, "-m", "autosynth.synth"]

    env = os.environ
    env["GITHUB_TOKEN"] = github_token

    library_args = [
        "--repository",
        library["repository"],
        "--synth-path",
        library.get("synth-path", ""),
        "--branch-suffix",
        library.get("branch-suffix", ""),
        "--pr-title",
        library.get("pr-title", ""),
    ]

    if library.get("metadata-path"):
        library_args.extend(["--metadata-path", library.get("metadata-path")])

    if library.get("deprecated-execution", False):
        library_args.append("--deprecated-execution")

    result = executor.run(
        command + library_args + library.get("args", []) + extra_args,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        encoding="utf-8",
        env=env,
    )
    error = result.returncode not in (0, synth.EXIT_CODE_SKIPPED)
    skipped = result.returncode == synth.EXIT_CODE_SKIPPED
    if error:
        logger.error(f"Synthesis failed for {library['name']}")
    return {
        "name": library["name"],
        "output": result.stdout,
        "error": error,
        "skipped": skipped,
    }


def make_report(name: str, results: typing.List[typing.Dict]) -> None:
    """Write an xunit report sponge_log.xml to the current directory.

    Arguments:
        name {str} - Name of the report
        results {typing.List[typing.Dict]} - List of synth results
    """
    with open("report.xml.j2") as fh:
        template = jinja2.Template(fh.read())

    output = template.render(
        name=name,
        failures=len([result for result in results if result["error"]]),
        skips=len([result for result in results if result["skipped"]]),
        results=results,
    )

    with open("sponge_log.xml", "w") as fh:
        fh.write(output)


@functools.lru_cache()
def _list_issues_cached(gh, *args, **kwargs):
    """A caching wrapper for listing issues, so we don't expend our quota."""
    return list(gh.list_issues(*args, **kwargs))


def _close_issue(gh, repository: str, existing_issue: dict):
    if existing_issue is None:
        return

    logger.info(f"Closing issue: {existing_issue['url']}")
    gh.create_issue_comment(
        repository,
        issue_number=existing_issue["number"],
        comment="Autosynth passed, closing! :green_heart:",
    )
    gh.patch_issue(
        repository, issue_number=existing_issue["number"], state="closed",
    )


def _file_or_comment_on_issue(
    gh, name: str, repository: str, issue_title: str, existing_issue: dict, output: str
):
    message = f"""\
Here's the output from running `synth.py`:

```
{output}
```

Google internal developers can see the full log [here](https://sponge/{os.environ.get('KOKORO_BUILD_ID')}).
"""

    if not existing_issue:
        issue_details = (
            f"Hello! Autosynth couldn't regenerate {name}. :broken_heart:\n\n{message}"
        )
        labels = ["autosynth failure", "priority: p1", "type: bug"]

        api_label = gh.get_api_label(repository, name)
        if api_label:
            labels.append(api_label)

        issue = gh.create_issue(
            repository, title=issue_title, body=issue_details, labels=labels,
        )
        logger.info(f"Opened issue: {issue['url']}")

    # otherwise leave a comment on the existing issue.
    else:
        comment_body = (
            f"Autosynth is still having trouble generating {name}. :sob:\n\n{message}"
        )

        gh.create_issue_comment(
            repository, issue_number=existing_issue["number"], comment=comment_body,
        )
        logger.info(f"Updated issue: {existing_issue['url']}")


def report_to_github(gh, name: str, repository: str, error: bool, output: str) -> None:
    """Update GitHub with the status of the autosynth run.

    On failure, will either open a new issue or comment on an existing issue. On
    success, will close any open autosynth issues.

    Arguments:
        name {str} - Name of the library
        repository {str} - GitHub repository with the format [owner]/[repo]
        error {bool} - Whether or not the autosynth run failed
        output {str} - Output of the individual autosynth run
    """
    issue_title = f"Synthesis failed for {name}"

    # Get a list of all open autosynth failure issues, and check if there's
    # an existing one.
    open_issues = _list_issues_cached(
        gh, repository, state="open", label="autosynth failure"
    )
    existing_issues = [issue for issue in open_issues if issue["title"] == issue_title]
    existing_issue = existing_issues[0] if len(existing_issues) else None

    # If successful, close any outstanding issues for synthesizing this
    # library.
    if not error:
        _close_issue(gh, repository, existing_issue)
    # Otherwise, file an issue or comment on an existing issue for synthesis.
    else:
        _file_or_comment_on_issue(
            gh, name, repository, issue_title, existing_issue, output
        )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config")
    parser.add_argument("--github-token", default=os.environ.get("GITHUB_TOKEN"))
    parser.add_argument("extra_args", nargs=argparse.REMAINDER)

    args = parser.parse_args()

    config = None
    if os.path.exists(args.config):
        with open(args.config) as fh:
            config = yaml.load(fh)["libraries"]
    else:
        try:
            provider = importlib.import_module(args.config)
            config = provider.list_repositories()
        except (ImportError, AttributeError):
            pass

    if config is None:
        sys.exit("No configuration could be loaded.")

    gh = github.GitHub(args.github_token)

    results = []
    for library in config:
        result = synthesize_library(library, args.github_token, args.extra_args[1:])
        results.append(result)

        if library.get("no_create_issue"):
            continue

        try:
            report_to_github(
                gh=gh,
                name=library["name"],
                repository=library["repository"],
                error=result["error"],
                output=result["output"],
            )
        except requests.HTTPError:
            # ignore as GitHub commands already log errors on failure
            pass

    make_report(args.config, results)

    num_failures = len([result for result in results if result["error"]])
    if num_failures > 0:
        logger.error(f"Failed to synthesize {num_failures} job(s).")
        sys.exit(1)


if __name__ == "__main__":
    main()
