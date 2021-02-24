# Copyright 2021 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import yaml


def prepare_toc(product_name):
    toc_file = "target/docfx-yml/toc.yml"
    with open(toc_file, 'r') as yml_input:
        try:
            toc = yaml.safe_load(yml_input)

            # sort list of dict on dict key 'uid' value
            toc.sort(key=lambda x: x.get('uid'))

            # include index.md overview page
            overview = [
                {
                    'name': 'Overview',
                    'href': 'index.md'
                }
            ]
            toc = overview + toc

            # include product level hierarchy
            new_toc = [
                {
                    'name': product_name,
                    'items': toc
                }
            ]

            with open(toc_file, 'w') as f:
                # Add back necessary docfx comment YamlMime
                f.write("### YamlMime:TableOfContent\n")

                yaml.dump(new_toc, f, default_flow_style=False, sort_keys=False)

        except yaml.YAMLError as e:
            print('Error parsing toc file', toc_file)
            raise e


if __name__ == '__main__':
    prepare_toc(sys.argv[1])