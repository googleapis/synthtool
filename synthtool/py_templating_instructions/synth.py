import synthtool as s
from synthtool import gcp

common = gcp.CommonTemplates()
sample_files = common.py_samples(samples=True)
for path in sample_files:
    s.move(path, excludes=['noxfile.py'])