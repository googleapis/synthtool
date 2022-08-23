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
FROM gcr.io/cloud-devrel-public-resources/java8

# The OwlBot Java postprocessor does not rely on project's Java formatter.
# When you upgrade the formatter version, see the issue below for the required
# changes:
# https://github.com/googleapis/synthtool/issues/1502
ARG JAVA_FORMAT_VERSION=1.7

RUN apt-get install -y --no-install-recommends jq

COPY docker/owlbot/java/bin /owlbot/bin
COPY docker/owlbot/java/src /owlbot/src
COPY docker/owlbot/java/templates /owlbot/templates
COPY post-processor-changes.txt /post-processor-changes.txt
RUN cd /owlbot/src && \
    python3 -m pip install -r requirements.txt

ADD https://repo1.maven.org/maven2/com/google/googlejavaformat/google-java-format/${JAVA_FORMAT_VERSION}/google-java-format-${JAVA_FORMAT_VERSION}-all-deps.jar /owlbot/google-java-format.jar

###################### Install synthtool's requirements.
COPY . /synthtool/

WORKDIR /synthtool
RUN python3 -m pip install -e .

# Allow non-root users to run python
RUN chmod +rx /root/ /root/.pyenv && chmod +r /owlbot/google-java-format.jar

# Tell synthtool to pull templates from this docker image instead of from
# the live repo.
ENV SYNTHTOOL_TEMPLATES="/synthtool/synthtool/gcp/templates" \
    PYTHON_PATH="/owlbot/src"

WORKDIR /workspace

CMD [ "/owlbot/bin/entrypoint.sh" ]
