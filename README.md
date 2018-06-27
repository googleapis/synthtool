# SynthTool (for client libraries)

This tool helps to generate and layout cloud client libraries. 

## Installation

This tool requires Python 3.6. Either install it from python.org or use
pyenv to get 3.6.


```
git clone sso://devrel/cloud/libraries/tools/synthtool
cd synthtool
pip install .
```

## Basic usage

### Python

To start the process of generation, we need to clone the destination repository.

```
git clone git@github.com:GoogleCloudPlatform/google-cloud-python.git
cd google-cloud-python
cd {cloud-package}
```

If a `synth.py` script is not present at the root of the package, we will need
to author a synth.py script. You can grab one from another package 
(for instance tasks in python) or start from scratch.

We run synthtool as follows:
```
python synth.py
```

Once you run synthtool without errors:
- Investigate the changes it made just to be certain everything looks reasonable
- run the unit tests (nox)
- commit and push the changes to a branch and open a PR!

### Node.js
- TODO. Should be similar to Python

### Ruby
- TODO. Should be similar to Python
