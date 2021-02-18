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

# Version 0.1.1

# build from the root of this repo:
# docker build -t gcr.io/cloud-devrel-kokoro-resources/owlbot-nodejs -f docker/owlbot/nodejs/Dockerfile .
FROM python:3.6.12-buster

WORKDIR /

######################## Install nodejs.
# Use `nvm` to bootstrap the installation of node.js and npm.
# To learn more: https://github.com/nvm-sh/nvm
RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.35.3/install.sh | bash

# Use the latest LTS version of nodejs.  This can change over time, but
# should prevent the need to modify this file every year.
# The "npm config set unsafe-perm true" is necessary because npm will refuse to perform
# some operations if the user is running as root.  The root user of a docker image
# doesn't have root permissions on the machine, so it's safe to execute them.
# I learned this from https://geedew.com/What-does-unsafe-perm-in-npm-actually-do/
RUN /bin/bash -c "source /root/.nvm/nvm.sh && nvm install --lts && npm config set unsafe-perm true"

###################### Install synthtool's requirements.
COPY requirements.txt /synthtool/requirements.txt
RUN pip install -r /synthtool/requirements.txt

# Put synthtool in the PYTHONPATH so owlbot.py scripts will find it.
ENV PYTHONPATH="/synthtool"

# Tell synthtool to pull templates from this docker image instead of from
# the live repo.
ENV SYNTHTOOL_TEMPLATES="/synthtool/synthtool/gcp/templates"

# Copy synthtool.
COPY synthtool /synthtool/synthtool
COPY autosynth /synthtool/autosynth
COPY docker /synthtool/docker
# Install dependencies used for post processing:
# * gts/typescript are used for linting.
# * google-gax is used for compiling protos.
RUN /bin/bash -c "source /root/.nvm/nvm.sh && mkdir node_modules && npm i gts@3.1.0 google-gax@2.10.3 typescript@3.9.9"

ENTRYPOINT [ "/bin/bash" ]
CMD [ "/synthtool/docker/owlbot/nodejs/entrypoint.sh" ]
