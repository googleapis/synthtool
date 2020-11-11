# build from the root of this repo:
# docker build -t gcr.io/cloud-devrel-kokoro-resources/synthtool -f autosynth/docker/Dockerfile .
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

# bazel requires zip.
RUN apt-get update
RUN apt-get install zip

# Install java
RUN curl -L https://download.java.net/java/GA/jdk15.0.1/51f4f36ad4ef43e39d0dfdbaf6549e32/9/GPL/openjdk-15.0.1_linux-x64_bin.tar.gz -o java.tar.gz
RUN gunzip java.tar.gz
RUN tar xf java.tar
ENV PATH="/jdk-15.0.1/bin:${PATH}"

# Install synthtool's requirements.
COPY requirements.txt /synthtool/requirements.txt
RUN pip install -r /synthtool/requirements.txt

# Put synthtool in the PYTHONPATH so we can invoke it with `python -m autosynth`.
ENV PYTHONPATH="/synthtool"

# Copy synthtool.
COPY synthtool /synthtool/synthtool
COPY autosynth /synthtool/autosynth

# By default, display instructions on how to run synthtool.
CMD ["/bin/cat", "/synthtool/autosynth/docker/README.txt"]