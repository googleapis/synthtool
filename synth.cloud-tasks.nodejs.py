import synthtool as s
import synthtool_gcp as gcp
import logging
from pathlib import Path
import subprocess

logging.basicConfig(level=logging.DEBUG)

gapic = gcp.GAPICGenerator("/tmp/synthtool-googleapis")
common = gcp.CommonTemplates()

# tasks has two product names, and a poorly named artman yaml
v2beta2_library = gapic._generate_code(
    'tasks', 'v2beta2', 'nodejs',
    artman_yaml_name='artman_cloudtasks.yaml',
    artman_output_name='cloudtasks-v2beta2')

s.copy(v2beta2_library)

# Node.js Package.json fixes
# "name": "@google-cloud/${api}",
# "repository": "googleapis/nodejs-${api}",
s.replace(Path('package.json'),
          '"name": "tasks"',
          '"name": "@googleapis/tasks"')
s.replace(Path('package.json'),
          '"repository": "GoogleCloudPlatform/google-cloud-node",',
          '"repository": "googleapis/nodejs-tasks",')


# #
# # Node Specific Setup.
# # Seems maybe repo tools doesn't work until this has a remote.
# #

# # README and Repo tools setup
# # Repo tools requires this be a git repo.
# # subprocess.run(['git', 'init'])
# # subprocess.run(['git', 'commit', '-a', '-m', '"Generated Code"'])
# subprocess.run([
#     'curl',
#     '-o',
#     'package-setup.js',
#     'https://gist.githubusercontent.com/alexander-fenster/8e28b40658fa517dc3c0873edc31e233/raw/package-setup.js'],
#     stdout=subprocess.DEVNULL)
# subprocess.run(['node', 'package-setup.js'])

# # prettify and lint
# subprocess.run(['npm', 'run', 'prettier'])
# subprocess.run(['npm', 'run', 'lint'])

# # Generate scaffolding for repo
# subprocess.run(['npm', 'run', 'generate-scaffolding'])

# # Currently creating by following:
# # https://docs.google.com/document/d/1IYag0PlkkH_6J7c1QX-oMIT9jY7Xhl2iwCTloIBj_qo/edit#heading=h.u971za9ida1a
