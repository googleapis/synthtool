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

# Version 0.3.0

# build from the root of this repo:
# docker build -t gcr.io/repo-automation-bots/owlbot-nodejs -f docker/owlbot/nodejs/Dockerfile .
FROM python:3.10.12-bookworm
RUN echo $(pwd)
RUN echo $(ls -a)
WORKDIR /

###################### Install nodejs.
RUN curl https://nodejs.org/dist/v18.17.0/node-v18.17.0-linux-x64.tar.xz > /tmp/nodejs.tar.xz
RUN tar -C /usr/local --strip-components=1 -xJf /tmp/nodejs.tar.xz
RUN rm -f /tmp/nodejs.tar.xz
ENV PATH "$PATH:/usr/local/bin"

###################### Install synthtool's requirements.
COPY requirements.txt /synthtool/requirements.txt
RUN pip install --require-hashes -r /synthtool/requirements.txt

# Put synthtool in the PYTHONPATH so owlbot.py scripts will find it.
ENV PYTHONPATH="/synthtool"

# Tell synthtool to pull templates from this docker image instead of from
# the live repo.
ENV SYNTHTOOL_TEMPLATES="/synthtool/synthtool/gcp/templates"

# Copy synthtool.
COPY synthtool /synthtool/synthtool
COPY docker /synthtool/docker
COPY post-processor-changes.txt /post-processor-changes.txt

# Update permissions so non-root users won't see errors.
RUN find /synthtool -exec chmod a+r {} \;
RUN find /synthtool -type d -exec chmod a+x {} \;

# Install dependencies used for post processing:
# * gts/typescript are used for linting.
# * google-gax and gapic-tools are used for compiling protos.
COPY package.json /package.json
RUN cd /synthtool && mkdir node_modules && cd ../
RUN echo $(pwd)
RUN echo $(ls -a)
RUN npm install --prefix synthtool/node_modules  --ignore-scripts -g

ENTRYPOINT [ "/bin/bash" ]
CMD [ "/synthtool/docker/owlbot/nodejs/entrypoint.sh" ]
