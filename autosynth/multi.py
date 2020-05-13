#!/usr/bin/env python3.6

"""Synthesizes multiple libraries and reports status."""

import argparse
import functools
import importlib
import os
import subprocess
import sys

import jinja2
import yaml

from autosynth import executor, github
from autosynth.log import logger


def synthesize_library(library, github_token, extra_args):
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
    return {
        "name": library["name"],
        "output": result.stdout,
        "error": result.returncode not in (0, 28),
    }


def make_report(name, results):
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

        gh.create_issue(
            repository, title=issue_title, body=issue_details, labels=labels,
        )

    # otherwise leave a comment on the existing issue.
    else:
        comment_body = (
            f"Autosynth is still having trouble generating {name}. :sob:\n\n{message}"
        )

        gh.create_issue_comment(
            repository, issue_number=existing_issue["number"], comment=comment_body,
        )


def report_to_github(gh, name: str, repository: str, error: bool, output: str):
    issue_title = f"Synthesis failed for {name}"

    # Get a list of all open autosynth failure issues, and check if there's
    # an existing one.
    open_issues = _list_issues_cached(
        gh, repository, state="open", label="autosynth failure"
    )
    existing_issue = [issue for issue in open_issues if issue["title"] == issue_title]
    existing_issue = existing_issue[0] if len(existing_issue) else None

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

        report_to_github(
            gh=gh,
            name=library["name"],
            repository=library["repository"],
            error=result["error"],
            output=result["output"],
        )

    make_report(args.config, results)

    num_failures = len([result for result in results if result["error"]])
    if num_failures > 0:
        logger.error(f"Failed to synthesize {num_failures} job(s).")
        sys.exit(1)


if __name__ == "__main__":
    main()
