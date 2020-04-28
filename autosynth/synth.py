#!/usr/bin/env python3.6
# Copyright 2020 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Synthesizes a single library and sends a PR."""

import argparse
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import typing

import autosynth
import autosynth.flags
from autosynth import git, github, git_source
from autosynth.abstract_source import AbstractSourceVersion
from autosynth.synthesizer import Synthesizer, AbstractSynthesizer
from autosynth.change_pusher import (
    AbstractChangePusher,
    ChangePusher,
    SquashingChangePusher,
)
from autosynth.log import logger
from typing import Dict, Sequence

WORKING_REPO = "working_repo"

IGNORED_FILE_PATTERNS = [
    # Ignore modifications to synth.metadata in any directory, this still allows *new*
    # synth.metadata files to be added.
    re.compile(r"M (.*?)synth.metadata")
]


def load_metadata(metadata_path: str):
    path = pathlib.Path(metadata_path)
    if not path.exists():
        return {}
    return json.loads(path.read_text())


class FlatVersion:
    """A pair of (group_number, version).

    See flatten_source_versions for more context.
    """

    def __init__(self, group_number: int, version: AbstractSourceVersion):
        self.group_number = group_number
        self.version = version
        self.sort_key = (self.version.get_timestamp(), group_number)
        self.merged = False


def flatten_and_sort_source_versions(
    source_versions: typing.Sequence[typing.Sequence[AbstractSourceVersion]],
) -> typing.List[FlatVersion]:
    """Flattens groups of versions.

    For example, for the input:
    [[a, b], [c, d, e]]

    The return value will be:
    [(1, a), (1, b), (2, c), (2, d), (2, e)]
    sorted by version timestamp.

    The return value is easy to binary search, because it's linear.  But it's
    still easy to see which group each version is a member of.
    """
    flat_list = []
    for number, group in enumerate(source_versions):
        for version in group:
            flat_list.append(FlatVersion(number, version))
    flat_list.sort(key=lambda v: v.sort_key)
    return flat_list


def generate_apply_table(versions: typing.List[FlatVersion]) -> Sequence[Sequence[int]]:
    """Return a table that answers the following question:

    When applying version i, what versions from other sources do I also need to apply?
    The answer is the youngest versions of other sources that are older than version i.
    When all versions of another source are younger than version i, then choose the
    oldest version.

    So for two sources with the following versions:
    A: 1   3  4  5
    B:   2         6

    This function will return:
    [[1, 2], [1, 2], [3, 2], [4, 2], [5, 2], [5, 6]

    Precalcuting a table takes O(n) time and avoids an O(n^2) loop later.
    """
    table = []
    vmap: Dict[int, int] = {}
    # Traverse the list of versions from beginning to end, recording the most recent
    # version from each group.
    for i, version in enumerate(versions):
        vmap = dict(vmap)
        vmap[version.group_number] = i
        table.append(vmap)
    # Fill in missing versions in the beginning.
    for amap in reversed(table[:-1]):
        new_map = dict(vmap)
        new_map.update(amap)
        amap.update(new_map)
        vmap = amap
    return [list(d.values()) for d in table]


class VersionZero:
    """Info recorded to implement optimization of only synthing version zero once
    across multiple sources."""

    def __init__(self):
        self.branch_name: str = ""
        self.has_changes: bool = False


class SynthesizeLoopToolbox:
    """A convenient collection of state and functions called by synthesize_loop."""

    def __init__(
        self,
        source_versions: typing.Sequence[typing.Sequence[AbstractSourceVersion]],
        branch: str,
        temp_dir: str,
        metadata_path: str,
        synth_path: str,
    ):
        self._temp_dir = temp_dir
        self._metadata_path = metadata_path
        self._preconfig_path = os.path.join(temp_dir, "preconfig.json")
        self._synth_path = synth_path or ""

        self.branch = branch
        self.version_groups = [list(group) for group in source_versions]
        self.versions = flatten_and_sort_source_versions(source_versions)
        self.apply_table = generate_apply_table(self.versions)
        self.commit_count = 0
        # Set the environment variable to point to the preconfig.json file.
        self.environ = dict(os.environ)
        self.environ["SYNTHTOOL_PRECONFIG_FILE"] = self._preconfig_path
        self.source_name = ""  # Only non-empty for forks
        self.version_zero = VersionZero()

    def apply_version(self, version_index: int) -> None:
        """Applies one version from each group."""
        preconfig: typing.Dict[str, typing.Any] = {}  # protocol message
        for i in self.apply_table[version_index]:
            self.versions[i].version.apply(preconfig)
        with open(self._preconfig_path, "wt") as preconfig_file:
            json.dump(preconfig, preconfig_file)

    def sub_branch(self, version_index: int) -> str:
        """Returns the name of the sub-branch for the version."""
        return f"{self.branch}-{version_index}"

    def checkout_new_branch(self, index: int) -> None:
        """Create a new branch for the version."""
        subprocess.check_call(["git", "checkout", "-b", self.sub_branch(index)])

    def checkout_sub_branch(self, index: int):
        """Check out the branch for the version."""
        subprocess.check_call(["git", "checkout", self.sub_branch(index)])

    def patch_merge_version(self, index: int, comment=None) -> bool:
        """Merges the given version into the current branch using a patch merge."""
        sub_branch = self.sub_branch(index)
        if self.git_branches_differ("HEAD", sub_branch):
            patch_file_path = os.path.join(self._temp_dir, f"{sub_branch}.patch")
            git.patch_merge(sub_branch, patch_file_path)
            git.commit_all_changes(
                comment or self.versions[index].version.get_comment()
            )
            self.commit_count += 1
            self.versions[index].merged = True
            return True
        return False

    def git_branches_differ(self, branch_a: str, branch_b: str):
        """Compares two git branches ignoring synth.metadata file."""
        return git_branches_differ(branch_a, branch_b, self._metadata_path)

    def fork(self) -> typing.List["SynthesizeLoopToolbox"]:
        """Create a new toolbox for each source.

        Each fork contains the same list of sources.  In each fork, only one
        source contains its full list of versions.  The other sources contain
        the oldest version only.
        Returns:
            [typing.List[SynthesizeLoopToolbox]] -- A toolbox for each source.
        """
        forks = []
        for i, group in enumerate(self.version_groups):
            new_groups = [[g[0]] for g in self.version_groups]
            new_groups[i] = self.version_groups[i]
            source_name = self.version_groups[i][0].get_source_name()
            fork_branch = f"{self.branch}-{source_name}"
            fork = SynthesizeLoopToolbox(
                new_groups,
                fork_branch,
                self._temp_dir,
                self._metadata_path,
                self._synth_path,
            )
            fork.source_name = source_name
            fork.commit_count = self.commit_count
            fork.version_zero = self.version_zero
            subprocess.check_call(["git", "branch", fork_branch])
            forks.append(fork)
        return forks

    def synthesize_version_in_new_branch(
        self, synthesizer: AbstractSynthesizer, index: int
    ) -> bool:
        """Invokes the synthesizer on the version specified by index.

        Stores the result in a new branch.
        Leaves the current branch unchanged.
        Arguments:
            synthesizer {AbstractSynthesizer} -- A synthesizer.
            index {int} -- index into self.versions

        Returns:
            bool -- True if the code generated differs.
        """
        self.apply_version(index)
        self.checkout_new_branch(index)
        try:
            if 0 == index:
                if self.version_zero.branch_name:
                    # Reuse version zero built for another source.
                    subprocess.check_call(
                        ["git", "merge", "--ff-only", self.version_zero.branch_name]
                    )
                    return self.version_zero.has_changes

            if index + 1 == len(self.versions):
                # The youngest version.  Let exceptions raise because the
                # current state is broken, and there's nothing we can do.
                synthesizer.synthesize(self.environ)
            else:
                synthesizer.synthesize_and_catch_exception(self.environ)
            # Save changes into the sub branch.
            i_has_changes = has_changes()
            if i_has_changes:
                git.commit_all_changes(self.versions[index].version.get_comment())
            if 0 == index:
                # Record version zero info so other sources can reuse.
                self.version_zero.branch_name = self.sub_branch(0)
                self.version_zero.has_changes = i_has_changes
            return i_has_changes
        finally:
            subprocess.check_call(["git", "reset", "--hard", "HEAD"])
            subprocess.check_call(["git", "checkout", self.branch])

    def count_commits_with_context(self) -> int:
        """Returns the number of commits that could be traced to a source version."""
        return self.commit_count - 1 if self.versions[0].merged else self.commit_count

    def push_changes(self, change_pusher: AbstractChangePusher) -> None:
        """Composes a PR title and pushes changes to github."""
        if self.commit_count < 1:
            return
        pr_title = _compose_pr_title(
            self.count_commits_with_context(), self._synth_path, self.source_name
        )
        change_pusher.push_changes(self.commit_count, self.branch, pr_title)


def _compose_pr_title(
    commits_with_context_count: int, synth_path: str, source_name: str
) -> str:
    """Compose a title for the pull request for changes merged by this toolbox.

    Arguments:
        commits_with_context_count {int} -- Commits with context about what triggered
        synth_path {str} -- Path to directory that contains synth.py, or empty.
        source_name {str} -- Name of the source, or empty.

    Returns:
        str -- The PR title.
    """
    synth_path_space = f"{synth_path} " if synth_path else ""
    synth_path_squared = f"[{synth_path}] " if synth_path else ""
    if 1 == commits_with_context_count:
        return synth_path_squared + git.get_commit_subject()
    elif source_name:
        return (
            f"[CHANGE ME] Re-generated {synth_path_space}to pick up changes "
            f"from {source_name}."
        )
    else:
        return (
            f"[CHANGE ME] Re-generated {synth_path_space}to pick up changes "
            "in the API or client library generator."
        )


def synthesize_loop(
    toolbox: SynthesizeLoopToolbox,
    multiple_prs: bool,
    change_pusher: AbstractChangePusher,
    synthesizer: AbstractSynthesizer,
) -> int:
    """Loops through all source versions and creates a commit for every version
    changed that caused a change in the generated code.

    Arguments:
        toolbox {SynthesizeLoopToolbox} -- a toolbox
        multiple_prs {bool} -- True to create one pull request per source.
        change_pusher {AbstractChangePusher} -- Used to push changes to github.
        synthesizer {AbstractSynthesizer} -- Invokes synthesize.

    Returns:
        int -- Number of commits committed to this repo.
    """
    if not toolbox.versions:
        return 0  # No versions, nothing to synthesize.
    try:
        if multiple_prs:
            commit_count = 0
            for fork in toolbox.fork():
                if change_pusher.check_if_pr_already_exists(fork.branch):
                    continue
                subprocess.check_call(["git", "checkout", fork.branch])
                synthesize_inner_loop(fork, synthesizer)
                commit_count += fork.commit_count
                if fork.source_name == "self" or fork.count_commits_with_context() > 0:
                    fork.push_changes(change_pusher)
            return commit_count
    except Exception:
        pass  # Fall back to non-forked loop below.
    synthesize_inner_loop(toolbox, synthesizer)
    toolbox.push_changes(change_pusher)
    return toolbox.commit_count


def synthesize_inner_loop(
    toolbox: SynthesizeLoopToolbox, synthesizer: AbstractSynthesizer,
):
    # Synthesize with the most recent version of all the sources.
    if not toolbox.synthesize_version_in_new_branch(
        synthesizer, len(toolbox.versions) - 1
    ):
        return  # No differences, nothing more to do.

    # Synthesize with the oldest version of all the sources.
    if 1 == len(toolbox.versions) or toolbox.synthesize_version_in_new_branch(
        synthesizer, 0
    ):
        comment = """changes without context

        autosynth cannot find the source of changes triggered by earlier changes in this
        repository, or by version upgrades to tools such as linters."""
        toolbox.patch_merge_version(0, comment)

    # Binary search the range.
    synthesize_range(toolbox, synthesizer)


def synthesize_range(
    toolbox: SynthesizeLoopToolbox, synthesizer: AbstractSynthesizer
) -> None:
    # Loop through all the individual source versions to see which ones triggered a change.
    # version_ranges is a stack.  The code below maintains the invariant
    # that it's sorted with the oldest ranges being popped first.
    # That way, we apply changes to the current branch in order from oldest
    # to youngest.
    version_ranges: typing.List[typing.Tuple[int, int]] = [
        (0, len(toolbox.versions) - 1)
    ]
    while version_ranges:
        old, young = version_ranges.pop()
        if young == old + 1:
            # The base case: Found a version that triggered a change.
            toolbox.patch_merge_version(young)
            continue
        if not toolbox.git_branches_differ(
            toolbox.sub_branch(old), toolbox.sub_branch(young)
        ):
            continue  # No difference; no need to search range.
        # Select the middle version to synthesize.
        middle = (young - old) // 2 + old
        toolbox.synthesize_version_in_new_branch(synthesizer, middle)
        version_ranges.append((middle, young))
        version_ranges.append((old, middle))


def git_branches_differ(branch_a: str, branch_b: str, metadata_path: str) -> bool:
    # Check to see if any files besides synth.metadata were added, modified, deleted.
    proc = subprocess.run(
        ["git", "diff", f"{branch_a}..{branch_b}", "--", f":(exclude){metadata_path}"],
        stdout=subprocess.PIPE,
        universal_newlines=True,
    )
    proc.check_returncode()
    if bool(proc.stdout):
        return True
    # Check to see if synth.metadata was added.
    proc = subprocess.run(
        ["git", "diff", f"{branch_a}..{branch_b}", "--", metadata_path],
        stdout=subprocess.PIPE,
        universal_newlines=True,
    )
    proc.check_returncode()
    diff_text = proc.stdout
    pattern = f"^--- /dev/null"
    return bool(re.search(pattern, diff_text, re.MULTILINE))


def has_changes():
    output = subprocess.check_output(["git", "status", "--porcelain"])
    output = output.decode("utf-8").strip()
    logger.info("Changed files:")
    logger.info(output)

    # Parse the git status output. Ignore any blank lines.
    changed_files = [line.strip() for line in output.split("\n") if line]

    # Ignore any files that are in our IGNORED_FILES set and only report
    # that there are changes if these ignored files are not the *only* changed
    # files.
    filtered_changes = []
    for file in changed_files:
        for expr in IGNORED_FILE_PATTERNS:
            if expr.match(file):
                break
        else:
            filtered_changes.append(file)

    return True if filtered_changes else False


def main() -> int:
    """
    Returns:
        int -- Number of commits committed to the repo.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        return _inner_main(temp_dir)


def _inner_main(temp_dir: str) -> int:
    """
    Returns:
        int -- Number of commits committed to the repo.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--github-user", default=os.environ.get("GITHUB_USER"))
    parser.add_argument("--github-email", default=os.environ.get("GITHUB_EMAIL"))
    parser.add_argument("--github-token", default=os.environ.get("GITHUB_TOKEN"))
    parser.add_argument(
        "--repository", default=os.environ.get("REPOSITORY"), required=True
    )
    parser.add_argument("--synth-path", default=os.environ.get("SYNTH_PATH"))
    parser.add_argument("--metadata-path", default=os.environ.get("METADATA_PATH"))
    parser.add_argument(
        "--deprecated-execution",
        default=False,
        action="store_true",
        help="If specified, execute synth.py directly instead of synthtool. This behavior is deprecated.",
    )
    parser.add_argument(
        "--branch-suffix", default=os.environ.get("BRANCH_SUFFIX", None)
    )
    parser.add_argument("--pr-title", default="")
    parser.add_argument("extra_args", nargs=argparse.REMAINDER)

    args = parser.parse_args()

    gh = github.GitHub(args.github_token)

    branch = "-".join(filter(None, ["autosynth", args.branch_suffix]))

    pr_title = args.pr_title or (
        f"[CHANGE ME] Re-generated {args.synth_path or ''} to pick up changes in "
        f"the API or client library generator."
    )
    change_pusher: AbstractChangePusher = ChangePusher(args.repository, gh, branch)

    if os.path.exists(WORKING_REPO):
        shutil.rmtree(WORKING_REPO)
    git.clone_repo(f"https://github.com/{args.repository}.git", WORKING_REPO)

    os.chdir(WORKING_REPO)

    git.configure_git(args.github_user, args.github_email)

    git.setup_branch(branch)

    if args.synth_path:
        os.chdir(args.synth_path)

    metadata_path = os.path.join(args.metadata_path or "", "synth.metadata")

    flags = autosynth.flags.parse_flags()
    # Override flags specified in synth.py with flags specified in environment vars.
    for key in flags.keys():
        env_value = os.environ.get(key, "")
        if env_value:
            flags[key] = False if env_value.lower() == "false" else env_value

    metadata = load_metadata(metadata_path)
    multiple_commits = flags[autosynth.flags.AUTOSYNTH_MULTIPLE_COMMITS]
    multiple_prs = flags[autosynth.flags.AUTOSYNTH_MULTIPLE_PRS]
    if (not multiple_commits and not multiple_prs) or not metadata:
        if change_pusher.check_if_pr_already_exists(branch):
            return 0

        synth_log = Synthesizer(
            metadata_path,
            args.extra_args,
            deprecated_execution=args.deprecated_execution,
        ).synthesize()

        if not has_changes():
            logger.info("No changes. :)")
            sys.exit(28)

        git.commit_all_changes(pr_title)
        change_pusher.push_changes(1, branch, pr_title, synth_log)
        return 1

    else:
        if not multiple_prs and change_pusher.check_if_pr_already_exists(branch):
            return 0  # There's already an existing PR

        # Enumerate the versions to loop over.
        sources = metadata.get("sources", [])
        source_versions = [
            git_source.enumerate_versions_for_working_repo(metadata_path, sources)
        ]
        # Add supported source version types below:
        source_versions.extend(
            git_source.enumerate_versions(sources, pathlib.Path(temp_dir))
        )

        # Prepare to call synthesize loop.
        synthesizer = Synthesizer(
            metadata_path, args.extra_args, args.deprecated_execution, "synth.py"
        )
        x = SynthesizeLoopToolbox(
            source_versions, branch, temp_dir, metadata_path, args.synth_path
        )
        if not multiple_commits:
            change_pusher = SquashingChangePusher(change_pusher)

        # Call the loop.
        commit_count = synthesize_loop(x, multiple_prs, change_pusher, synthesizer)

        if commit_count == 0:
            logger.info("No changes. :)")
            sys.exit(28)

        return commit_count


if __name__ == "__main__":
    main()
