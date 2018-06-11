import synthtool as s
import synthtool_gcp as gcp
import logging
from pathlib import Path

logging.basicConfig(level=logging.DEBUG)

gapic = gcp.GAPICGenerator()
common = gcp.CommonTemplates()

# tasks has two product names, and a poorly named artman yaml
v1_library = gapic._generate_code(
    'iot', 'v1', 'python',
    artman_yaml_name='artman_cloudiot.yaml'
)
s.copy(v1_library)


# Fix nox.py params for unit/system tests
# https://github.com/googleapis/gapic-generator/issues/2017
s.replace(
    'nox.py',
    "@nox.parametrize\('py', .*(\ndef unit\(session, py\):)",
    "@nox.parametrize('py', ['2.7', '3.5', '3.6', '3.7'])\g<1>")
s.replace(
    'nox.py',
    "@nox.parametrize\('py', .*(\ndef system\(session, py\):)",
    "@nox.parametrize('py', ['2.7', '3.7'])\g<1>")


# Correct calls to routing_header
# https://github.com/googleapis/gapic-generator/issues/2016
s.replace(
    "google/cloud/iot_v1/gapic/device_manager_client.py",
    "routing_header\(",
    "routing_header.to_grpc_metadata(")

# metadata in tests in none but should be empty list.
# https://github.com/googleapis/gapic-generator/issues/2014
s.replace(
    "google/cloud/*/gapic/*_client.py",
    'def .*\(([^\)]+)\n.*metadata=None\):\n\s+"""(.*\n)*?\s+"""\n',
    '\g<0>'
    '        if metadata is None:\n'
    '            metadata = []\n'
    '        metadata = list(metadata)\n')

# line 380 and 755 have an issue with empty objects trying to get attrs
# https://github.com/googleapis/gapic-generator/issues/2015
# empty objects trying to get attrs
# https://github.com/googleapis/gapic-generator/issues/2015
s.replace(
    "google/cloud/*/gapic/*_client.py",
    "(^        )(routing_header = google.api_core.gapic_v1.routing_header"
    ".to_grpc_metadata\(\n)"
    "(\s+)(\[\('[a-z\_]*?\.name', )([a-z\_]*?)(.name\)\], \)\n)"
    "(\s+metadata.append\(routing_header\)\n)",
    "\g<1>if hasattr(\g<5>, 'name'):\n"
    "\g<1>    \g<2>\g<3>    \g<4>\g<5>\g<6>    \g<7>"
)


# metadata in tests in none but should be empty list.
# https://github.com/googleapis/gapic-generator/issues/2014


# empty objects trying to get attrs
# https://github.com/googleapis/gapic-generator/issues/2015


# TODO: Generation failing due to Device.name not being a valid
# call to `device = {}`
