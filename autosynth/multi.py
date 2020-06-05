#!/usr/bin/env python3.6

"""Synthesizes multiple libraries and reports status."""

import argparse
import functools
import importlib
import os
import pathlib
import requests
import subprocess
import sys
import typing
import jinja2
import yaml

from autosynth import executor, github, synth
from autosynth.log import logger


# Callable type to help dependency inject for testing
Runner = typing.Callable[
    [typing.List[str], typing.Any, pathlib.Path], typing.Tuple[int, bytes]
]


def _execute(
    command: typing.List[str], env: typing.Any, log_file_path: pathlib.Path
) -> typing.Tuple[int, bytes]:
    """Helper to wrap command invocation for testing"""
    # Ensure the logfile directory exists
    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_file_path, "wb+") as log_file:
        result = executor.run(
            command=command,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            check=False,
            encoding="utf-8",
            env=env,
        )
    with open(log_file_path, "rb") as fp:
        return (result.returncode, fp.read())


def synthesize_library(
    library: typing.Dict,
    github_token: str,
    extra_args: typing.List[str],
    base_log_path: pathlib.Path,
    runner: Runner = _execute,
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

    log_file_path = base_log_path / library["repository"] / "sponge_log.log"
    # run autosynth in a separate process
    (returncode, output) = runner(
        command + library_args + library.get("args", []) + extra_args,
        env,
        log_file_path,
    )
    error = returncode not in (0, synth.EXIT_CODE_SKIPPED)
    skipped = returncode == synth.EXIT_CODE_SKIPPED
    if error:
        logger.error(f"Synthesis failed for {library['name']}")
    return {
        "name": library["name"],
        "output": output.decode("utf-8"),
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
    gh, name, repository, issue_title, existing_issue, output
):
    # GitHub rejects issues with bodies > 64k
    output_to_report = output[-10000:]
    message = f"""\
Here's the output from running `synth.py`:

```
{output_to_report}
```

Google internal developers can see the full log [here](http://sponge/{os.environ.get('KOKORO_BUILD_ID')}).
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


def load_config(
    config: str,
) -> typing.Optional[typing.List[typing.Dict[str, typing.Any]]]:
    """Load configuration from either a configuration YAML or from a module.

    If a yaml path is provided, it must return a top level "libraries" entry
    which contains a list of repository definitions.

    If a module is provided, it will invoke list_repositories() on the
    module which should return a list of repository definitions.

    A repository definition is a dictionary which contains:
    * name {str} -- Required. The name of the repo/client
    * repository {str} -- Required. GitHub repository with the format [owner]/[repo]
    * synth-path {str} -- Optional. Path within the repository to the synth.py file.
    * branch-suffix {str} -- Optional. When opening a pull request, use this suffix for
        branch name
    * metadata-path {str} -- Optional. Path to location of synth.metadata file.
    * deprecated-execution {bool} -- Optional. If set, will invoke synthtool with the
        synthtool binary rather than as a module. Defaults to False.
    * no_create_issue {bool} -- Optional. If set, will not manage GitHub issues when
        autosynth fails for any reason. Defaults to False.

    Arguments:
        config {str} -- Path to configuration YAML or module name

    Returns:
        List[Dict[str, Any]] - List of library configurations to synthesize
        None - The configuration file doesn't exist and no module found
    """
    if os.path.exists(config):
        with open(config) as fh:
            return yaml.load(fh)["libraries"]
    else:
        try:
            provider = importlib.import_module(config)
            return provider.list_repositories()  # type: ignore
        except (ImportError, AttributeError):
            pass
    return None


def synthesize_libraries(
    libraries: typing.Dict,
    gh: github.GitHub,
    github_token: str,
    extra_args: typing.List[str],
    base_log_path: pathlib.Path,
    runner: Runner = _execute,
) -> typing.List[typing.Dict]:
    """Synthesize all libraries and report any error as GitHub issues.

    Arguments:
        libraries {typing.List[typing.Dict]} -- Autosynth configuration. See load_config
            for more information on the structure.
        gh {github.GitHub} -- GitHub API wrapper
        github_token {str} -- API Token for GitHub
        extra_args {typing.List[str]} -- Additional command line arguments to pass to autosynth.synth

    Returns:
        typing.List[typing.Dict] -- List of results for each autosynth.synth run.
    """
    results = []
    for library in libraries:
        result = synthesize_library(
            library, github_token, extra_args[1:], base_log_path, runner
        )
        results.append(result)

        # skip issue management
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
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config")
    parser.add_argument("--github-token", default=os.environ.get("GITHUB_TOKEN"))
    parser.add_argument("extra_args", nargs=argparse.REMAINDER)

    args = parser.parse_args()

    config = load_config(args.config)
    if config is None:
        sys.exit("No configuration could be loaded.")

    gh = github.GitHub(args.github_token)

    base_log_path = pathlib.Path("./logs")
    results = synthesize_libraries(
        config, gh, args.github_token, args.extra_args[1:], base_log_path
    )
    make_report(args.config, results)

    num_failures = len([result for result in results if result["error"]])
    if num_failures > 0:
        logger.error(f"Failed to synthesize {num_failures} job(s).")
        failure_percent = 100 * num_failures / len(results)
        if failure_percent < 10:
            pass  # It's most likely an issue with a few APIs.
        else:
            sys.exit(1)  # Raise the attention of autosynth maintainers.


if __name__ == "__main__":
    main()
