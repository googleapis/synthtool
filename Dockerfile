# Copyright 2023 Google LLC
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

FROM python:3.10.6-buster

COPY . /synthtool/

WORKDIR /synthtool
# remove postprocessor images
RUN rm -rdf /synthtool/docker

RUN python3 -m pip install -e .
RUN python3 -m pip install -r requirements.in

# Allow non-root users to run python
RUN chmod +rx /root/

WORKDIR /workspace

ENV SYNTHTOOL_TEMPLATES="/synthtool/synthtool/gcp/templates"
CMD [ "python3" ]
