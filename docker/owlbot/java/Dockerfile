# Copyright 2021 Google LLC
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

# build from the root of this repo:
FROM gcr.io/cloud-devrel-kokoro-resources/java8

ARG JAVA_FORMAT_VERSION=1.7

COPY docker/owlbot/java/scripts/*.sh /java/
ADD https://repo1.maven.org/maven2/com/google/googlejavaformat/google-java-format/${JAVA_FORMAT_VERSION}/google-java-format-${JAVA_FORMAT_VERSION}-all-deps.jar /java/google-java-format.jar

###################### Install synthtool's requirements.
COPY . /synthtool/

WORKDIR /synthtool
RUN python3 -m pip install -e .

# Tell synthtool to pull templates from this docker image instead of from
# the live repo.
ENV SYNTHTOOL_TEMPLATES="/synthtool/synthtool/gcp/templates"

COPY docker/owlbot/java/entrypoint.sh /synthtool/entrypoint.sh

WORKDIR /workspace

ENTRYPOINT [ "/synthtool/entrypoint.sh" ]
