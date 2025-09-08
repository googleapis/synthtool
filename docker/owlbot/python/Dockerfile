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

# Version 0.2.0

# build from the root of this repo:
# docker build -t gcr.io/repo-automation-bots/owlbot-python -f docker/owlbot/python/Dockerfile .
FROM marketplace.gcr.io/google/ubuntu2404

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    # Essential for compiling C code
    build-essential \
    git \
    wget \
    ca-certificates \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libffi-dev \
    libsqlite3-dev \
    libreadline-dev \
    # ------------------------------------------------------
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install multiple Python versions from source. `make altinstall` is used to
# prevent replacing the system's default python binary.
# TODO(http://github.com/googleapis/gapic-generator-python/issues/2435): Remove `3.10.18` when the linked issue is resolved.
RUN for PYTHON_VERSION in 3.10.18 3.13.5; do \
    wget https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz && \
    tar -xvf Python-${PYTHON_VERSION}.tgz && \
    cd Python-${PYTHON_VERSION} && \
    ./configure --enable-optimizations --prefix=/usr/local && \
    make -j$(nproc) && \
    make altinstall && \
    cd / && \
    rm -rf Python-${PYTHON_VERSION}* \
    ; done

# Install pip for each python version
# TODO(http://github.com/googleapis/gapic-generator-python/issues/2435): Remove `3.10` when the linked issue is resolved.
RUN wget --no-check-certificate -O /tmp/get-pip.py 'https://bootstrap.pypa.io/get-pip.py' && \
    for PYTHON_VERSION in 3.10 3.13; do \
        python${PYTHON_VERSION} /tmp/get-pip.py; \
    done && \
    rm /tmp/get-pip.py


WORKDIR /

###################### Install synthtool's requirements.
COPY requirements.txt /synthtool/requirements.txt
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
RUN find /synthtool -exec chmod a+r {} \;
RUN find /synthtool -type d -exec chmod a+x {} \;

ENTRYPOINT [ "/bin/bash" ]
CMD [ "/synthtool/docker/owlbot/python/entrypoint.sh" ]

