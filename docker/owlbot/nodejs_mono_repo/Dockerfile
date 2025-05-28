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

## Install Essential Tools, Python 3.11, and xz-utils

# Update apt and install core tools.
# This includes git, curl, and 'xz-utils' (needed for Node.js tarball decompression).
# python3, python3-pip, and python3-venv are installed to provide Python 3.11 and
# the tools for creating virtual environments.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    git \
    curl \
    xz-utils \
    python3 \
    python3-pip \
    python3-venv && \
    rm -rf /var/lib/apt/lists/*

# Verify Python installation and ensure pip is available.
# 'python3' command will now point to Python 3.11.
RUN python3 --version
RUN python3 -m pip --version

## Install Node.js

# Download and extract Node.js directly into /usr/local.
# The 'curl' command includes '-fsSL' for silent, fail-fast, and redirect-following behavior.
RUN curl -fsSL https://nodejs.org/dist/v18.17.0/node-v18.17.0-linux-x64.tar.xz -o /tmp/nodejs.tar.xz && \
    tar -C /usr/local --strip-components=1 -xJf /tmp/nodejs.tar.xz && \
    rm -f /tmp/nodejs.tar.xz

# Add Node.js binaries to the PATH.
ENV PATH "$PATH:/usr/local/bin"

## Install Synthtool and Dependencies

# Create a Python virtual environment for synthtool's dependencies.
# This isolates your Python packages from the system Python, preventing conflicts.
ENV VIRTUAL_ENV=/opt/venv/synthtool
RUN python3 -m venv $VIRTUAL_ENV
# Add the virtual environment's bin directory to the PATH. This effectively "activates"
# the venv for all subsequent commands in this and future RUN layers.
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy requirements.txt and install Python dependencies into the virtual environment.
# Since we're in the venv, 'pip' directly refers to the venv's pip.
COPY requirements.txt /synthtool/requirements.txt
RUN pip install --require-hashes -r /synthtool/requirements.txt

# Set PYTHONPATH to ensure synthtool can be found by Python scripts.
# Include the virtual environment's site-packages for completeness.
ENV PYTHONPATH="/synthtool:$VIRTUAL_ENV/lib/python3.11/site-packages"

# Configure synthtool to use templates from this image.
ENV SYNTHTOOL_TEMPLATES="/synthtool/synthtool/gcp/templates"

# Copy synthtool source code and associated Docker files.
COPY synthtool /synthtool/synthtool
COPY docker /synthtool/docker
COPY post-processor-changes.txt /post-processor-changes.txt

# Update file permissions to prevent errors for non-root users.
RUN find /synthtool -exec chmod a+r {} \; && \
    find /synthtool -type d -exec chmod a+x {} \;

# Install Node.js dependencies for post-processing.
RUN cd /synthtool && mkdir node_modules && npm i gts@6.0.2 google-gax@5.0.1-rc.0 \
    typescript@5.8.3 @google-cloud/typeless-sample-bot@1.3.3 gapic-tools@1.0.1

ENTRYPOINT [ "/bin/bash", "/synthtool/docker/owlbot/nodejs_mono_repo/entrypoint.sh" ]