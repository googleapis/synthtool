from synthtool.sources import git


result = git.clone(
    'git@github.com:googleapis/googleapis.git')

print(result)

from synthtool import shell

shell.run(['git', 'clone', 'meep'])
