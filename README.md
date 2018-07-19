# SynthTool (for client libraries)

This tool helps to generate and layout cloud client libraries. 

## Installation

This tool requires Python 3.6. Either install it from python.org or use
pyenv to get 3.6.


```
# Install latest

python3 -m pip install --user --upgrade git+https://github.com/GoogleCloudPlatform/synthtool.git

# Install stable
python3 -m pip install --user --upgrade gcp-synthtool
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
Node.js generation is similar to python. For an example `synth.py` you can look at https://github.com/googleapis/nodejs-speech/blob/master/synth.py.

### Ruby
- TODO. Should be similar to Python


## Features
### Templating
Synthtool supports template files using jinja. As an example let's look at node.js. The templates for node can be found at `/synthtool/gcp/templates/node_library/`. The following is taken from a node.js synth script.

```
common_templates = gcp.CommonTemplates()

templates = common_templates.node_library(package_name="@google-cloud/speech")
s.copy(templates)
```

`package_name` is a keyword arg that is used by a jinja template. Jinja uses `{{ package_name }}` to customize the template for a specific package. You can add additionaly keyword args as necessary.
