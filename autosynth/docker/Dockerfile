# build from the root of this repo:
# docker build -t python-synthtool -f dockerfiles/python/Dockerfile .
FROM python:3.6.12-buster

WORKDIR /

# Upgrade the NPM version
RUN npm install -g npm

# Install bazel 3.0.0
RUN mkdir -p /bazel
RUN curl -L https://github.com/bazelbuild/bazel/releases/download/3.0.0/bazel-3.0.0-linux-x86_64 -o /bazel/bazel
RUN chmod +x /bazel/bazel
ENV PATH="/bazel:${PATH}"

# Install synthtool's requirements.
COPY requirements.txt /synthtool/requirements.txt
RUN pip install -r /synthtool/requirements.txt

# Copy synthtool.
COPY synthtool /synthtool/synthtool
COPY autosynth /synthtool/autosynth


