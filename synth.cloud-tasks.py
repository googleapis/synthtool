import synthtool as s
import synthtool_gcp as gcp
import logging


logging.basicConfig(level=logging.DEBUG)

gapic = gcp.GAPICGenerator("/tmp/synthtool-googleapis")
common = gcp.CommonTemplates()

# tasks has two product names, and a poorly named artman yaml
v2beta2_library = gapic._generate_code(
    'tasks', 'v2beta2', 'python',
    artman_yaml_name='artman_cloudtasks.yaml',
    artman_output_name='cloudtasks-v2beta2')

s.copy(v2beta2_library)


# s.copy(v1_library / 'tests/gapic/myapi_v1', 'tests/gapic/myapi_v1')
# s.copy(v1_library / 'docs/reference', 'docs/v1')
# s.copy(v1p1beta1_library,  'google/cloud/myapi_v1p1beta1')
# s.copy(v1p1beta1_library, 'tests/gapic/myapi_v1p1beta1')
# s.copy(v1p1beta1_library / 'docs/reference', 'docs/v1p1beta1')

# FUTURE add code to stitch together __init__.py
# common.render('python/speech/__init__.py', versions=['v1', 'v1beta1'])

# FUTURE Add code to stitch together RST
# common.render('python/docs/index.rst', versions=['v1', 'v1beta1'])
