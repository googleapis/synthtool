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

import os
import typing
import pathlib
from autosynth.executor import Executor, DEFAULT_EXECUTOR

GLOBAL_GITIGNORE = """
__pycache__/
*.py[cod]
*$py.class
"""

GLOBAL_GITIGNORE_FILE = os.path.expanduser("~/.autosynth-gitignore")


def clone_repo(
    source_url: str, target_path: str, executor: Executor = DEFAULT_EXECUTOR
) -> None:
    """Clones a remote repo to a local directory.

    Arguments:
        source_url {str} -- Url of the remote repo
        target_path {str} -- Local directory name for the clone
    """
    executor.run(
        ["git", "clone", "--single-branch", source_url, "--", target_path], check=True
    )


def configure_git(user: str, email: str, executor: Executor = DEFAULT_EXECUTOR) -> None:
    with open(GLOBAL_GITIGNORE_FILE, "w") as fh:
        fh.write(GLOBAL_GITIGNORE)

    executor.run(
        ["git", "config", "--global", "core.excludesfile", GLOBAL_GITIGNORE_FILE],
        check=True,
    )
    executor.run(["git", "config", "user.name", user], check=True)
    executor.run(["git", "config", "user.email", email], check=True)
    executor.run(["git", "config", "push.default", "simple"], check=True)


def setup_branch(branch: str, executor: Executor = DEFAULT_EXECUTOR) -> None:
    executor.run(["git", "checkout", "-b", branch], check=True)

    executor.run(["git", "branch", "-f", branch], check=True)
    executor.run(["git", "checkout", branch], check=True)


def get_last_commit_to_file(
    file_path: str, executor: Executor = DEFAULT_EXECUTOR
) -> str:
    """Returns the commit hash of the most recent change to a file."""
    parent_dir = pathlib.Path(file_path).parent
    return executor.run(
        ["git", "log", "--pretty=format:%H", "-1", "--no-decorate", file_path],
        cwd=parent_dir,
        check=True,
    ).strip()


def get_commit_shas_since(
    sha: str, dir: str, executor: Executor = DEFAULT_EXECUTOR
) -> typing.List[str]:
    """Gets the list of shas for commits committed after the given sha.

    Arguments:
        sha {str} -- The sha in the git history.
        dir {str} -- An absolute path to a directory in the git repository.

    Returns:
        typing.List[str] -- A list of shas.  The 0th sha is sha argument (the oldest sha).
    """
    shas = executor.run(
        ["git", "log", f"{sha}..HEAD", "--pretty=%H", "--no-decorate"],
        cwd=dir,
        check=True,
    ).split()
    shas.append(sha)
    shas.reverse()
    return shas


def commit_all_changes(message, executor: Executor = DEFAULT_EXECUTOR):
    executor.run(["git", "add", "-A"], check=True)
    executor.run(["git", "commit", "-m", message], check=True)


def push_changes(branch, executor: Executor = DEFAULT_EXECUTOR):
    executor.run(["git", "push", "--force", "origin", branch], check=True)


def get_repo_root_dir(repo_path: str, executor: Executor = DEFAULT_EXECUTOR) -> str:
    """Given a path to a file or dir in a repo, find the root directory of the repo.

    Arguments:
        repo_path {str} -- Any path into the repo.

    Returns:
        str -- The repo's root directory.
    """
    path = pathlib.Path(repo_path)
    if not path.is_dir():
        path = path.parent
    return executor.run(
        ["git", "rev-parse", "--show-toplevel"], cwd=str(path), check=True
    ).strip()


def patch_merge(
    branch_name: str,
    patch_file_path: str,
    git_repo_dir: str = None,
    executor: Executor = DEFAULT_EXECUTOR,
) -> None:
    """Merges a branch via `git diff | git apply`.

    Does not commit changes.  Modifies files only.
    Arguments:
        branch_name {str} -- The other branch to merge into this one.
        patch_file_path {str} -- The path where the patch file will be (over)written.

    Keyword Arguments:
        git_repo_dir {str} -- The repo directory (default: current working directory)
    """
    executor.run(
        ["git", "diff", "HEAD", branch_name],
        log_file_path=patch_file_path,
        cwd=git_repo_dir,
        check=True,
    )
    if os.stat(patch_file_path).st_size:
        executor.run(["git", "apply", patch_file_path], cwd=git_repo_dir, check=True)


def get_commit_subject(
    repo_dir: str = None, sha: str = None, executor: Executor = DEFAULT_EXECUTOR
) -> str:
    """Gets the subject line of the a commit.

    Keyword Arguments:
        repo_dir {str} -- a directory in the repo; None means use cwd. (default: {None})
        sha {str} -- the sha of the commit.  None means the most recent commit.

    Returns:
        {str} -- the subject line
    """
    lines = executor.run(
        ["git", "log", "-1", "--no-decorate", "--format=%B"] + ([sha] if sha else []),
        cwd=repo_dir,
        check=True,
    ).splitlines()
    return lines[0].strip() if lines else ""
