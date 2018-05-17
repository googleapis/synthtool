import synthtool as s
import synthtool_gcp as gcp

gapic = gcp.GAPICGenerator()
common = gcp.CommonTemplates()

v1_library = gapic.py_library('myapi', 'v1')
v1p1beta1_library = gapic.py_library('myapi', 'v1beta1')

library_files = common.py_library(package_name='myapi')

# copy all library files and layout identically at dest
s.copy(library_files)
s.copy(v1_library / 'google/cloud/myapi_v1')
s.copy(v1_library / 'tests/gapic/myapi_v1')
s.copy(v1_library / 'docs/reference', 'docs/v1')
s.copy(v1p1beta1_library,  'google/cloud/myapi_v1p1beta1')
s.copy(v1p1beta1_library, 'tests/gapic/myapi_v1p1beta1')

# copy docs/reference to docs/v1p1beta1
s.copy(v1p1beta1_library / 'docs/reference', 'docs/v1p1beta1')

common.render('python/docs/index.rst', versions=['v1', 'v1beta1'])
