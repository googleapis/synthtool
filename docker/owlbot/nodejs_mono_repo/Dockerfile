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
    xz-utils

# Install pyenv dependencies
RUN apt-get update && \
    apt-get install -y make build-essential libssl-dev zlib1g-dev libbz2-dev \
    libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev libncursesw5-dev \
    xz-utils tk-dev libffi-dev liblzma-dev && \
    apt-get upgrade -y

WORKDIR /root

# Install pyenv
RUN curl -L -o /tmp/pyenv.tar.gz https://github.com/pyenv/pyenv/archive/refs/tags/v2.6.22.tar.gz && \
    mkdir -p /root/.pyenv && \
    tar -xzvf /tmp/pyenv.tar.gz -C /root/.pyenv --strip-components=1 && \
    echo 'eval "$(pyenv init -)"' >> /root/.profile && \
    echo 'eval "$(pyenv virtualenv-init -)"' >> /root/.profile

ENV PATH="/root/.pyenv/bin:/root/.pyenv/shims:${PATH}"

## Install Node.js from apt-get

# Add NodeSource APT repository for Node.js v18
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Remove unnecessary cross-spawn from npm to resolve CVE-2024-21538
RUN rm -r /usr/lib/node_modules/npm/node_modules/cross-spawn

# Verify Node.js and npm installations
RUN node --version
RUN npm --version

## Install Synthtool and Dependencies

# Install python
RUN pyenv install 3.13.12 && \
    pyenv global 3.13.12 

# This is needed to upgrade pip in the following path
# /root/.pyenv/versions/3.13.12/lib/python3.13/site-packages/
RUN pip install --upgrade pip

# Create a Python virtual environment for synthtool's dependencies.
# This isolates your Python packages from the system Python, preventing conflicts.
ENV VIRTUAL_ENV=/opt/venv/synthtool
RUN python3 -m venv $VIRTUAL_ENV
# Add the virtual environment's bin directory to the PATH. This effectively "activates"
# the venv for all subsequent commands in this and future RUN layers.
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# This is needed to upgrade pip in the following path
# /opt/venv/synthtool/lib/python3.13/site-packages/
RUN pip install --upgrade pip

# TODO(https://github.com/python/cpython/issues/144538): This is
# need to address CVE-2026-1703 which requires pip 26.0
# as per https://github.com/advisories/GHSA-4xh5-x5gv-qwph.
# Remove this code once Python 3.13.13 is released which includes a fix.
RUN rm -rf /root/.pyenv/versions/3.13.12/lib/python3.13/ensurepip/_bundled/pip-25.3-py3-none-any.whl

# Copy requirements.txt and install Python dependencies into the virtual environment.
# Since we're in the venv, 'pip' directly refers to the venv's pip.
COPY requirements.txt /synthtool/requirements.txt
RUN pip install --require-hashes -r /synthtool/requirements.txt

# TODO: Remove this code once there is a newer version of virtualenv which does not include setuptools 75.3.2
# https://github.com/pypa/virtualenv/tree/20.36.1/src/virtualenv/seed/wheels/embed
# In the interim, remove the bundled setuptools 75.3.2 wheel
# since it does not include a fix for CVE-2025-47273/CVE-2025-47273.
RUN rm -rf /opt/venv/synthtool/lib/python3.13/site-packages/virtualenv/seed/wheels/embed/setuptools-75.3.2-py3-none-any.whl
# TODO: Remove this code once there is a newer version of virtualenv which does not include pip 25.0.1 and 25.3
# https://github.com/pypa/virtualenv/tree/20.36.1/src/virtualenv/seed/wheels/embed
# In the interim, remove the bundled pip wheel
# since it does not include a fix for CVE-2026-1703
RUN rm -rf /opt/venv/synthtool/lib/python3.13/site-packages/virtualenv/seed/wheels/embed/pip-25.3-py3-none-any.whl
RUN rm -rf /opt/venv/synthtool/lib/python3.13/site-packages/virtualenv/seed/wheels/embed/pip-25.0.1-py3-none-any.whl

# TODO: Remove this code once there is a newer version of virtualenv which does not include wheel 45.1
# https://github.com/pypa/virtualenv/tree/20.36.1/src/virtualenv/seed/wheels/embed
# In the interim, remove the bundled wheel 45.1
# since it does not include a fix for CVE-2026-24049
RUN rm -rf /opt/venv/synthtool/lib/python3.13/site-packages/virtualenv/seed/wheels/embed/wheel-0.45.1-py3-none-any.whl

# Set PYTHONPATH to ensure synthtool can be found by Python scripts.
# Include the virtual environment's site-packages for completeness.
ENV PYTHONPATH="/synthtool:$VIRTUAL_ENV/lib/python3.13/site-packages"

# Configure synthtool to use templates from this image.
ENV SYNTHTOOL_TEMPLATES="/synthtool/synthtool/gcp/templates"

# Copy synthtool source code and associated Docker files.
COPY synthtool /synthtool/synthtool
COPY docker /synthtool/docker
# COPY post-processor-changes.txt /post-processor-changes.txt

# Update file permissions to prevent errors for non-root users.
RUN find /synthtool -exec chmod a+r {} \; && \
    find /synthtool -type d -exec chmod a+x {} \;

RUN useradd -ms /bin/bash nonroot

# Change ownership of /synthtool and its contents to the nonroot user.
# This must happen as root, before switching users.
RUN chown -R nonroot:nonroot /synthtool

# Switch to the non-root user to run npm install.
USER nonroot

# Install Node.js dependencies as the non-root user.
WORKDIR /synthtool
RUN npm i gts@6.0.2 google-gax@5.1.0-rc.1 \
    typescript@5.8.3 @google-cloud/typeless-sample-bot@1.3.3 gapic-tools@1.0.2 \
    gapic-node-processing@latest

# Switch back to root if needed for subsequent steps.
USER root

# ... (any other commands that require root access) ...

ENTRYPOINT [ "/bin/bash", "/synthtool/docker/owlbot/nodejs_mono_repo/entrypoint.sh" ]