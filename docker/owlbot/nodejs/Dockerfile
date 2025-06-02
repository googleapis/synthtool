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

## Install Essential Tools, Python 3.11, and xz-utils

# Install necessary tools, the default Python 3 (which is 3.11 on Debian 12),
# python3-venv for virtual environments, and xz-utils for Node.js archives.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates \
    git \
    python3 \
    python3-pip \
    python3-venv \
    curl \
    xz-utils && \
    rm -rf /var/lib/apt/lists/*

# Verify Python installation and ensure pip is available.
# 'python3' command will now point to Python 3.11.
RUN python3 --version
RUN python3 -m pip --version


## Install Node.js from apt-get

# Add NodeSource APT repository for Node.js v18
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Verify Node.js and npm installations
RUN node --version
RUN npm --version

## Install Synthtool and Dependencies

# Create a Python virtual environment for synthtool dependencies.
# This isolates your Python packages from the system Python.
ENV VIRTUAL_ENV=/opt/venv/synthtool
RUN python3 -m venv $VIRTUAL_ENV
# Add the virtual environment's bin directory to the PATH. This effectively "activates"
# the venv for all subsequent commands in this and future RUN layers.
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copy requirements.txt and install Python dependencies into the virtual environment.
COPY requirements.txt /synthtool/requirements.txt
RUN pip install --require-hashes -r /synthtool/requirements.txt

# Set PYTHONPATH to ensure synthtool can be found by Python scripts.
# Include the virtual environment's site-packages for completeness, though
# the PATH modification often handles this for executables run directly.
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
RUN cd /synthtool && mkdir node_modules && npm install @google-cloud/typeless-sample-bot@1.3.3

## Entrypoint Configuration

# Set the entrypoint to a shell, and the default command to your entrypoint script.
ENTRYPOINT [ "/bin/bash" ]
CMD [ "/synthtool/docker/owlbot/nodejs/entrypoint.sh" ]