# SynthTool (for client libraries)
This tool helps to generate and layout cloud client libraries. Synthtool runs the [GAPIC (Generated API Client) Generator][GAPIC] via [Google API Artifact Manager (artman)][artman].

[GAPIC]: https://github.com/googleapis/gapic-generator
[artman]: https://github.com/googleapis/artman

## Installation

This tool requires Python 3.6. Either install it from [python.org][python_downloads] or use
[pyenv][] to get 3.6.

[python_downloads]: https://www.python.org/downloads/
[pyenv]: https://github.com/pyenv/pyenv

If you are using GAPIC generator `synthtool.gcp.GAPICGenerator` or DiscoGAPIC generator `synthtool.gcp.DiscoGAPICGenerator`, install [Docker][].

[Docker]: https://docs.docker.com/v17.09/engine/installation/#desktop

### Install latest

```
python3 -m pip install --user --upgrade git+https://github.com/googleapis/synthtool.git
```

## Basic usage
To start the process of generation, clone the destination repository.
```
git clone git@github.com:googleapis/google-cloud-python.git
cd google-cloud-python/
```

Navigate to the destination directory to generate the library.
```
cd tasks/
```

### Running `synthtool`
If a `synth.py` script is not present, create a new one.

You can create one from scratch or copy one from another library.
 - e.g. the `synth.py` for the Cloud Tasks API for [Python][python_tasks_synth_py],
[Java][java_tasks_synth_py], [Node.js][node_tasks_synth_py], [PHP][php_tasks_synth_py],
or [Ruby][ruby_tasks_synth_py].

Run `synthtool`:

```
python3 -m synthtool
```

After `synthtool` runs successfully:
 - Investigate the changes it made
 - Run the library tests
 - Commit and push the changes to a branch and open a Pull Request

Find examples below in different programming languages (Cloud Tasks API used as an example).

### Python
- Clone the destination repository:
  ```
  git clone git@github.com:googleapis/google-cloud-python.git
  cd google-cloud-python/
  ```
- Navigate to the destination directory to generate the library:
  ```
  cd tasks/
  ```
- Run `synthtool` to generate using the existing [`synth.py`][python_tasks_synth_py]
  file for the [Python Client for Cloud Tasks API][python_tasks_library]:
  ```
  python3 -m synthtool
  ```
- See the Python [Contributing Guide][python_contributing]
  or instructions to install dependencies, run tests, and submit a contribution.

[python_tasks_library]: https://github.com/googleapis/google-cloud-python/tree/master/tasks
[python_tasks_synth_py]: https://github.com/googleapis/google-cloud-python/blob/master/tasks/synth.py
[python_contributing]: https://github.com/googleapis/google-cloud-python/blob/master/CONTRIBUTING.rst

### Java
- Clone the destination repository:
  ```
  git clone git@github.com:googleapis/google-cloud-java.git
  cd google-cloud-java/
  ```
- Navigate to the destination directory to generate the library:
  ```
  cd google-cloud-clients/google-cloud-tasks/
  ```
- Run `synthtool` to generate using the existing [`synth.py`][java_tasks_synth_py]
  file for the [Google Cloud Java Client for Cloud Tasks][java_tasks_library]:
  ```
  python3 -m synthtool
  ```
- See the Java [Contributing Guide][java_contributing]
  or instructions to install dependencies, run tests, and submit a contribution.

[java_tasks_library]: https://github.com/googleapis/google-cloud-java/tree/master/google-cloud-clients/google-cloud-tasks
[java_tasks_synth_py]: https://github.com/googleapis/google-cloud-java/blob/master/google-cloud-clients/google-cloud-tasks/synth.py
[java_contributing]: https://github.com/googleapis/google-cloud-java/blob/master/CONTRIBUTING.md

### Node.js
- Clone the destination repository:
  ```
  git clone git@github.com:googleapis/nodejs-tasks.git
  cd nodejs-tasks/
  ```
- Run `synthtool` to generate using the existing [`synth.py`][node_tasks_synth_py]
  file for the [Google Cloud Tasks Node.js Client][node_tasks_library]:
  ```
  python3 -m synthtool
  ```
- See the Node.js [Contributing Guide][node_tasks_contributing]
  or instructions to install dependencies, run tests, and submit a contribution.

[node_tasks_library]: https://github.com/googleapis/nodejs-task
[node_tasks_synth_py]: https://github.com/googleapis/nodejs-tasks/blob/master/synth.py
[node_tasks_contributing]: https://github.com/googleapis/nodejs-tasks/blob/master/CONTRIBUTING.md

### PHP
- Clone the destination repository:
  ```
  git clone git@github.com:googleapis/google-cloud-php.git
  cd google-cloud-php/
  ```
- Navigate to the destination directory to generate the library:
  ```
  cd Tasks/
  ```
- Run `synthtool` to generate using the existing [`synth.py`][php_tasks_synth_py]
  file for the [Google Cloud Tasks client for PHP][php_tasks_library]:
  ```
  python3 -m synthtool
  ```
- See the PHP [Contributing Guide][php_contributing]
  or instructions to install dependencies, run tests, and submit a contribution.

[php_tasks_library]: https://github.com/googleapis/google-cloud-php/tree/master/Tasks
[php_tasks_synth_py]: https://github.com/googleapis/google-cloud-php/blob/master/Tasks/synth.py
[php_contributing]: https://github.com/googleapis/google-cloud-php/blob/master/CONTRIBUTING.md

### Ruby
- Clone the destination repository:
  ```
  git clone git@github.com:googleapis/google-cloud-ruby.git
  cd google-cloud-ruby/
  ```
- Navigate to the destination directory to generate the library:
  ```
  cd google-cloud-tasks/
  ```
- Run `synthtool` to generate using the existing [`synth.py`][ruby_tasks_synth_py]
  file for the [Ruby Client for Cloud Tasks API][ruby_tasks_library]:
  ```
  python3 -m synthtool
  ```
- See the Ruby [Contributing Guide][ruby_contributing]
  or instructions to install dependencies, run tests, and submit a contribution.

[ruby_tasks_library]: https://github.com/googleapis/google-cloud-ruby/tree/master/google-cloud-tasks
[ruby_tasks_synth_py]: https://github.com/googleapis/google-cloud-ruby/blob/master/google-cloud-tasks/synth.py
[ruby_contributing]: https://github.com/googleapis/google-cloud-ruby/blob/master/.github/CONTRIBUTING.md

## Features
### Templating
SynthTool supports template files using [Jinja](http://jinja.pocoo.org/).

Templates are found in subdirectories of [`synthtool/gcp/templates/`](synthtool/gcp/templates/)
for each language,
 - e.g. the template directories for [Python][python_templates],
[Node.js][node_templates], [PHP][php_tasks_synth_py], or [Ruby][ruby_templates].

[python_templates]: synthtool/gcp/templates/python_library/
[node_templates]: synthtool/gcp/templates/node_library/
[php_templates]: synthtool/gcp/templates/php_library/
[ruby_templates]:  synthtool/gcp/templates/ruby_library/

You can generate and copy templates using `gcp.CommonTemplates` in your `synth.py`:
```py
common_templates = gcp.CommonTemplates()

templates = common_templates.node_library()
s.copy(templates)
```

You can provide variables to templates as keyword arguments to the library generation method:

```py
common_templates = gcp.CommonTemplates()

templates = common_templates.node_library(version=5, show_version=True, previous_versions=[1,2,3,4])

s.copy(templates)
```

Template files can access any values provided, e.g.
 - `README.md.j2`
    ```py
    {% if show_version %}
    The version is {{ version }}

    {% if previous versions is defined %}
    Previous versions:
      {% for ver in previous_versions %}
      - {{ ver }}
      {% endfor %}
    {% endif %}
    {% endif %}
    ```

You can learn more about Jinga templating in the
[Template Designer Documentation](http://jinja.pocoo.org/docs/templates/).

### googleapis-private
SynthTool supports generation from googleapis/googleapis-private.

```py
gapic = gcp.GAPICGenerator()

library = gapic.node_library('speech', 'v1', private=True)
```
2FA is required to clone a private repo.

* **Using SSH:** Before running Synthtool, set the environment variable `AUTOSYNTH_USE_SSH` to `true`.

The repo will be cloned using SSH.
* **Using HTTPS:** Generate a [GitHub Personal Access Token](https://github.com/settings/tokens) with scope `repo`.
Run `synthtool`.

When GitHub prompts for your GitHub password, provide the access token instead.

```
synthtool > Cloning googleapis-private.
Username for 'https://github.com': busunkim96
Password for 'https://busunkim96@github.com':
```

### Artman Version
SynthTool uses the latest version of the [Artman Docker image](https://hub.docker.com/r/googleapis/artman).
You can change this by setting the environment variable `SYNTHTOOL_ARTMAN_VERSION` to the desired version tag.

```
export SYNTHTOOL_ARTMAN_VERSION=0.16.2
```

### GAPIC Generator Python Version
SynthTool uses the latest version of [gcr.io/gapic-images/gapic-generator-python](https://gcr.io/gapic-images/gapic-generator-python). You can change this by
setting the environment variable `SYNTHTOOL_GAPIC_GENERATOR_PYTHON_VERSION` to the desired version tag.

```
export SYNTHTOOL_GAPIC_GENERATOR_PYTHON_VERSION=0.22.0
```

Alternatively you can set the generator version by passing it to `gapic.py_library`.

```python
import synthtool as s
import synthtool.gcp as gcp

gapic = gcp.GAPICMicrogenerator()

library = gapic.py_library(
    "bigquery/connection", "v1beta1", generator_version="0.22.0"
)
```

### Local Googleapis
SynthTool supports generation from a local copy of googleapis.
Specify the path to `googleapis` in the environment variable `SYNTHTOOL_GOOGLEAPIS`.

```
export SYNTHTOOL_GOOGLEAPIS=path/to/local/googleapis
```

### Local GAPIC Generator
SynthTool supports generation from a local copy of [gapic-generator](https://github.com/googleapis/gapic-generator).
Specify the path to `gapic-generator` in the environment variable `SYNTHTOOL_GENERATOR`.

```
export SYNTHTOOL_GENERATOR=path/to/local/gapic-generator
```

Don't forget to compile `gapic-generator` before running SynthTool.

```
cd path/to/local/gapic-generator
./gradlew fatJar
```

### Local Template Files
SynthTool supports specifying a local directory of templates. Specify the patht to the root
template directory (not a SynthTool clone) in the environment variable `SYNTHTOOL_TEMPLATES`.

```
export SYNTHTOOL_TEMPLATES=path/to/local/templates
```

### Include .proto files
SynthTool supports copying .proto API definition files from googleapis.

```py
gapic = gcp.GAPICGenerator()

library = gapic.node_library('speech', 'v1', include_protos=True)
```

## Context-Aware Commits

Autosynth runs synthtool on your `synth.py` nightly or more frequently.
By default, it runs synthtool once, and if the generated code differs,
creates a PR with the differences.

Autosynth can also find which changes in upstream repositories triggered changes
in the generated code.  To enable this behavior (context-aware commits),
set one or both of the following flags in you synth.py file:

```py
AUTOSYNTH_MULTIPLE_COMMITS
AUTOSYNTH_MULTIPLE_PRS
```

### Example

Assume that since the library source code was last generated, A, B and X, Y 
were committed to googleapis and synthtool respectively, and they all triggered
changes in the generated library code.

| [googleapis](https://github.com/googleapis/googleapis) | [synthtool (templates)](https://github.com/googleapis/synthtool/tree/master/synthtool/gcp/templates) |
| :--------: | :-------------------: |
|  A         |  X                    |
|  B         |  Y                    |


Here's what autosynth will generate for each flag setting.

```py
AUTOSYNTH_MULTIPLE_COMMITS = True
```

Autosynth will create one PR, with a single commit for each original commit:
| PR |
| - |
| A |
| B |
| X |
| Y |

***

```py
AUTOSYNTH_MULTIPLE_COMMITS = True
AUTOSYNTH_MULTIPLE_PRS = True
```

Autosynth will create two PRs, with a single commit for each original commit:
| PR1 |
| - |
| A |
| B |

| PR2 |
| - |
| X |
| Y |


***

```py
AUTOSYNTH_MULTIPLE_PRS = True
```

Autosynth will create two PRs, with a single commit combining all the 
original commits.

| PR1 |
| - |
| AB |

| PR2 |
| - |
| XY |


## Helpful tips
### Where does the generated code go?
SynthTool will run [Artman](https://hub.docker.com/r/googleapis/artman) which will create generated code that
can be found at `~/.cache/synthtool/googleapis<-private>/artman_genfiles`. This is useful for figuring out
what it is you need to copy for your specific library.
