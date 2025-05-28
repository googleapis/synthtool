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
# docker build -t gcr.io/repo-automation-bots/owlbot-nodejs-mono-repo -f docker/owlbot/nodejs_mono_repo/Dockerfile .
FROM marketplace.gcr.io/google/debian12:latest

WORKDIR /

###################### Install build essentials, ca-certificates, and Python 3.10 from source.
# Ensure apt-get is updated and install ca-certificates first
# This ensures that subsequent HTTPS downloads (like for Python source or Node.js) work.
# Then install other build dependencies for Python and general utilities.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    build-essential \
    zlib1g-dev \
    libncurses5-dev \
    libgdbm-dev \
    libnss3-dev \
    libssl-dev \
    libreadline-dev \
    libffi-dev \
    libsqlite3-dev \
    wget \
    libbz2-dev \
    tk-dev \
    liblzma-dev \
    curl \
    git && \
    rm -rf /var/lib/apt/lists/*

# Download and install Python 3.10.12
ENV PYTHON_VERSION=3.10.12
RUN wget https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz -O /tmp/python.tgz && \
    tar -xzf /tmp/python.tgz -C /tmp && \
    cd /tmp/Python-${PYTHON_VERSION} && \
    ./configure --enable-optimizations --with-ensurepip=install && \
    make -j$(nproc) && \
    make altinstall && \
    rm -rf /tmp/python.tgz /tmp/Python-${PYTHON_VERSION}

# Verify Python installation and ensure pip is available
RUN python3.10 --version
RUN python3.10 -m pip --version

# Set Python 3.10 as the default 'python' command (optional, but convenient for general use)
# This will make 'python' point to 'python3.10', but it might not make 'pip' point to 'pip3.10' directly.
# The 'python3.10 -m pip' approach is more robust.
RUN update-alternatives --install /usr/local/bin/python python /usr/local/bin/python3.10 1

###################### Install nodejs.
# Node.js installation
RUN curl -fsSL https://nodejs.org/dist/v18.17.0/node-v18.17.0-linux-x64.tar.xz -o /tmp/nodejs.tar.xz && \
    tar -C /usr/local --strip-components=1 -xJf /tmp/nodejs.tar.xz && \
    rm -f /tmp/nodejs.tar.xz
ENV PATH "$PATH:/usr/local/bin"

###################### Install synthtool's requirements.
COPY requirements.txt /synthtool/requirements.txt
# CHANGE THIS LINE: Use python3.10 -m pip explicitly
RUN python3.10 -m pip install --require-hashes -r /synthtool/requirements.txt

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
RUN find /synthtool -exec chmod a+r {} \; && \
    find /synthtool -type d -exec chmod a+x {} \;

# Install dependencies used for post processing:
# * gts/typescript are used for linting.
# * google-gax and gapic-tools are used for compiling protos.
RUN cd /synthtool && mkdir node_modules && npm i gts@6.0.2 google-gax@5.0.1-rc.0 \
    typescript@5.8.3 @google-cloud/typeless-sample-bot@1.3.3 gapic-tools@1.0.1

ENTRYPOINT [ "/bin/bash", "/synthtool/docker/owlbot/nodejs_mono_repo/entrypoint.sh" ]