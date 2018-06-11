import synthtool as s
import synthtool_gcp as gcp
import logging
from pathlib import Path

logging.basicConfig(level=logging.DEBUG)

gapic = gcp.GAPICGenerator()
common = gcp.CommonTemplates()

# tasks has two product names, and a poorly named artman yaml
v2beta2_library = gapic._generate_code(
    'tasks', 'v2beta2', 'ruby',
    artman_yaml_name='artman_cloudtasks.yaml',
    artman_output_name='google-cloud-ruby/google-cloud-cloudtasks')

s.copy(v2beta2_library)

# Manually Done: 
# 1) added iam dependency
# 2) made tocs.json under docs. 
# 3) added package to toplevel gemfile