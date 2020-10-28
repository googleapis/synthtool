# build from the root of this repo:
# docker build -t python-synthtool -f autosynth/docker/Dockerfile .
FROM python:3.6.12-buster

WORKDIR /

# Install nodejs.
RUN curl -sL https://deb.nodesource.com/setup_15.x | bash -
RUN apt-get install -y nodejs

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


