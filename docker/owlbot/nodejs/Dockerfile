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
# docker build -t gcr.io/repo-automation-bots/owlbot-nodejs -f docker/owlbot/nodejs/Dockerfile .
FROM marketplace.gcr.io/google/debian12:latest
WORKDIR /

## Install Build Essentials, ca-certificates, and Python 3.10

# This step installs necessary tools and libraries, including Python 3.10
# directly from the Debian repositories.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    git \
    python3.10 \
    python3-pip \
    curl && \
    rm -rf /var/lib/apt/lists/*

# Verify Python installation and ensure pip is available.
RUN python3.10 --version
RUN python3.10 -m pip --version

# Set Python 3.10 as the default 'python' command using update-alternatives.
# python3 is usually symlinked to python3.10 so this step might not be strictly necessary,
# but it's good practice for consistency.
RUN update-alternatives --install /usr/local/bin/python python /usr/bin/python3.10 1
# Also set a pip3 alternative for convenience, linking to the python3.10 pip.
RUN update-alternatives --install /usr/local/bin/pip3 pip3 /usr/bin/pip3 1

## Install Node.js

# Download and extract Node.js directly into /usr/local.
# The 'curl' command includes '-fsSL' for silent, fail-fast, and redirect-following behavior.
RUN curl -fsSL https://nodejs.org/dist/v18.20.8/node-v18.20.8-linux-x64.tar.xz -o /tmp/nodejs.tar.xz && \
    tar -C /usr/local --strip-components=1 -xJf /tmp/nodejs.tar.xz && \
    rm -f /tmp/nodejs.tar.xz

# Add Node.js binaries to the PATH.
ENV PATH "$PATH:/usr/local/bin"

## Install Synthtool and Dependencies

# Copy the requirements file and install Python dependencies using pip.
# We explicitly use 'python3.10 -m pip' to ensure the correct pip is invoked.
COPY requirements.txt /synthtool/requirements.txt
RUN python3.10 -m pip install --require-hashes -r /synthtool/requirements.txt

# Set PYTHONPATH to ensure synthtool can be found by Python scripts.
ENV PYTHONPATH="/synthtool"

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
RUN cd /synthtool && mkdir node_modules && npm install @google-cloud/typeless-sample-bot@1.3.3

## Entrypoint Configuration

# Set the entrypoint to a shell, and the default command to your entrypoint script.
ENTRYPOINT [ "/bin/bash" ]
CMD [ "/synthtool/docker/owlbot/nodejs/entrypoint.sh" ]
