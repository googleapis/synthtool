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

import base64
from typing import Generator, Sequence, Dict, Optional

import requests
import typing

_GITHUB_ROOT: str = "https://api.github.com"


class GitHub:
    def __init__(self, token: str) -> None:
        self.session: requests.Session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/vnd.github.v3+json",
                "Authorization": f"Bearer {token}",
            }
        )

    def list_org_repos(self, org: str, type: str = None) -> Generator[Dict, None, None]:
        url = f"{_GITHUB_ROOT}/orgs/{org}/repos"

        while url:
            response = self.session.get(url, params={"type": type})
            response.raise_for_status()
            for item in response.json():
                yield item

            url = response.links.get("next", {}).get("url")

    def list_pull_requests(self, repository: str, **kwargs) -> Sequence[Dict]:
        url = f"{_GITHUB_ROOT}/repos/{repository}/pulls"
        response = self.session.get(url, params=kwargs)
        response.raise_for_status()
        return response.json()

    def create_pull_request(
        self, repository: str, branch: str, title: str, body: str = None
    ) -> typing.Dict[str, typing.Any]:
        url = f"{_GITHUB_ROOT}/repos/{repository}/pulls"
        logger.info(f"creating pull request to {repository} for branch {branch}")
        logger.debug(body)
        response = self.session.post(
            url,
            json={
                "title": title,
                "body": body,
                "head": branch,
                "base": "master",
                "maintainer_can_modify": True,
            },
        )
        response.raise_for_status()
        return response.json()

    def get_tree(self, repository: str, tree_sha: str = "master") -> Sequence[dict]:
        url = f"{_GITHUB_ROOT}/repos/{repository}/git/trees/{tree_sha}"
        response = self.session.get(url, params={})
        response.raise_for_status()
        return response.json()

    def get_contents(self, repository: str, path: str, ref: str = None) -> bytes:
        url = f"{_GITHUB_ROOT}/repos/{repository}/contents/{path}"
        response = self.session.get(url, params={"ref": ref})
        response.raise_for_status()
        return base64.b64decode(response.json()["content"])

    def list_files(self, repository: str, path: str, ref: str = None) -> Sequence[dict]:
        url = f"{_GITHUB_ROOT}/repos/{repository}/contents/{path}"
        response = self.session.get(url, params={"ref": ref})
        response.raise_for_status()
        return response.json()

    def check_for_file(self, repository: str, path: str, ref: str = None) -> bool:
        url = f"{_GITHUB_ROOT}/repos/{repository}/contents/{path}"
        response = self.session.head(url, params={"ref": ref})

        if response.status_code == 200:
            return True
        else:
            return False

    def create_release(
        self,
        repository: str,
        tag_name: str,
        target_committish: str,
        name: str,
        body: str,
    ) -> Dict:
        url = f"{_GITHUB_ROOT}/repos/{repository}/releases"
        response = self.session.post(
            url,
            json={
                "tag_name": tag_name,
                "target_committish": target_committish,
                "name": name,
                "body": body,
            },
        )
        response.raise_for_status()
        return response.json()

    def create_pull_request_comment(
        self, repository: str, pull_request_number: int, comment: str
    ) -> Dict:
        repo_url = f"{_GITHUB_ROOT}/repos/{repository}"
        url = f"{repo_url}/issues/{pull_request_number}/comments"
        response = self.session.post(url, json={"body": comment})
        response.raise_for_status()
        return response.json()

    def list_issues(self, repository: str, **kwargs) -> Generator[Dict, None, None]:
        url = f"{_GITHUB_ROOT}/repos/{repository}/issues"

        while url:
            response = self.session.get(url, params=kwargs)
            response.raise_for_status()
            for item in response.json():
                yield item

            url = response.links.get("next", {}).get("url")

    def create_issue(
        self, repository: str, title: str, body: str, labels: Sequence[str]
    ) -> Dict:
        url = f"{_GITHUB_ROOT}/repos/{repository}/issues"
        response = self.session.post(
            url, json={"title": title, "body": body, "labels": labels}
        )
        response.raise_for_status()
        return response.json()

    def patch_issue(self, repository: str, issue_number: int, **kwargs) -> Dict:
        url = f"{_GITHUB_ROOT}/repos/{repository}/issues/{issue_number}"
        response = self.session.patch(url, json=kwargs)
        response.raise_for_status()
        return response.json()

    def create_issue_comment(
        self, repository: str, issue_number: int, comment: str
    ) -> Dict:
        repo_url = f"{_GITHUB_ROOT}/repos/{repository}"
        url = f"{repo_url}/issues/{issue_number}/comments"
        response = self.session.post(url, json={"body": comment})
        response.raise_for_status()
        return response.json()

    def replace_issue_labels(
        self, repository: str, issue_number: str, labels: Sequence[str]
    ) -> dict:
        url = f"{_GITHUB_ROOT}/repos/{repository}/issues/{issue_number}/labels"
        response = self.session.put(url, json={"labels": labels})
        response.raise_for_status()
        return response.json()

    def update_pull_labels(
        self, pull: dict, add: Sequence[str] = None, remove: Sequence[str] = None
    ) -> dict:
        """Updates labels for a github pull, adding and removing labels as needed."""
        label_names = set([label["name"] for label in pull["labels"]])
        if add:
            label_names = label_names.union(add)
        if remove:
            label_names = label_names.difference(remove)
        return self.replace_issue_labels(
            repository=pull["base"]["repo"]["full_name"],
            issue_number=pull["number"],
            labels=list(label_names),
        )

    def get_labels(self, repository: str) -> Sequence[str]:
        """Returns labels for a repository"""
        url = f"{_GITHUB_ROOT}/repos/{repository}/labels"
        labels = []

        while url:
            response = self.session.get(url)
            response.raise_for_status()
            for item in response.json():
                labels.append(item["name"])

            url = response.links.get("next", {}).get("url")

        return labels

    def get_api_label(self, repository: str, synth_path: str) -> Optional[str]:
        """Try to match the synth path to an api: * label"""
        if synth_path == "":
            return None

        api_labels = filter(lambda label: "api" in label, self.get_labels(repository))
        synth_path = synth_path.replace("_", "").lower()

        for label in api_labels:
            if synth_path in label:
                return label

        return None
