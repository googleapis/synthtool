import synthtool as s
import synthtool_gcp as gcp
import logging
from pathlib import Path

logging.basicConfig(level=logging.DEBUG)

gapic = gcp.GAPICGenerator("/tmp/synthtool-googleapis")
common = gcp.CommonTemplates()

# tasks has two product names, and a poorly named artman yaml
v1_library = gapic._generate_code(
    'iot', 'v1', 'python',
    artman_yaml_name='artman_cloudiot.yaml'
)
s.copy(v1_library)

# add import for grpc
s.replace(
    Path("google/cloud/iot_v1/gapic/device_manager_client.py"),
    "from google.cloud.iot_v1.proto import device_manager_pb2",
    "\g<0>\nfrom google.cloud.iot_v1.proto import device_manager_pb2_grpc")

# Correct path to stub
s.replace(
    Path("google/cloud/iot_v1/gapic/device_manager_client.py"),
    "device_manager_pb2.DeviceManagerStub",
    "device_manager_pb2_grpc.DeviceManagerStub")

# Correct calls to routing_header
s.replace(
    Path("google/cloud/iot_v1/gapic/device_manager_client.py"),
    "routing_header\(",
    "routing_header.to_grpc_metadata(")

# TODO: Generation failing due to Device.name not being a valid
# call to `device = {}`
