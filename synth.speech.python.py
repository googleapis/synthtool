import synthtool as s
import synthtool_gcp as gcp
import logging
logging.basicConfig()

gapic = gcp.GAPICGenerator()
common = gcp.CommonTemplates()

v1_library = gapic.py_library('speech', 'v1')
v1beta1_library = gapic.py_library('speech', 'v1beta1')
v1p1beta1_library = gapic.py_library('speech', 'v1p1beta1')


# FUTURE: add templating for library files
# library_files = common.py_library(package_name='myapi')

# copy all library files and layout identically at current directory
# s.copy(library_files)

s.copy(v1beta1_library / 'google/cloud/speech_v1beta1',
       'google/cloud/speech_v1beta1')
s.copy(v1p1beta1_library / 'google/cloud/speech_v1p1beta1',
       'google/cloud/speech_v1p1beta1')

# copy v1 last. this will result in this getting the default configurations.
s.copy(v1_library)

# s.copy(v1_library / 'tests/gapic/myapi_v1', 'tests/gapic/myapi_v1')
# s.copy(v1_library / 'docs/reference', 'docs/v1')
# s.copy(v1p1beta1_library,  'google/cloud/myapi_v1p1beta1')
# s.copy(v1p1beta1_library, 'tests/gapic/myapi_v1p1beta1')
# s.copy(v1p1beta1_library / 'docs/reference', 'docs/v1p1beta1')

# FUTURE add code to stitch together __init__.py
# common.render('python/speech/__init__.py', versions=['v1', 'v1beta1'])

# FUTURE Add code to stitch together RST
# common.render('python/docs/index.rst', versions=['v1', 'v1beta1'])
