# Java Post-Processing Docker Image

Docker image used for bootstrapping/post-processing. Running this on
should:

1. Generate common templates
2. Write any missing `pom.xml` files or update with new detected modules
3. Restore or create `clirr-ignored-differences.xml` files after a new release
4. Restore license header years on generated files.
5. Run our standard `google-java-format` plugin.

## Usage

### Running locally

```bash
docker run --rm -v $(pwd):/workspace --user "$(id -u):$(id -g)" gcr.io/repo-automation-bots/owlbot-java
```

### Building the image

#### Local Docker

From the root of the synthtool repository, run:

```bash
synthtool$ docker build -f docker/owlbot/java/Dockerfile .
...
Removing intermediate container e6d071e39d1b
 ---> a7d7e0c80b00
Successfully built a7d7e0c80b00
```

"a7d7e0c80b00" is the ID of the container image build. Try running the
postprocessor image with a target repository.
Here is an example with java-aiplatform repository  below:

```bash
java-aiplatform$ git checkout -b test_postprocessor origin/main
branch 'test_postprocessor' set up to track 'origin/main'.
Switched to a new branch 'test_postprocessor'
java-aiplatform$ docker run --rm -v $(pwd):/workspace a7d7e0c80b00
...
Reformatting source...
...done
java-aiplatform$ git diff
... (shows the generated file differences) ...
```

This manual confirmation identifies syntax errors in Python scripts and the
templates.

#### Cloud Build
This image is built via Cloud Build. From the root of this repository, run:

```bash
gcloud builds submit --config=docker/owlbot/java/cloudbuild.yaml
```

### Rebuilding Golden Test Fixtures

To rebuild the golden test fixtures:

1. Delete the `golden` directory.
2. Copy the `input` directory recursively to `golden`
3. [Run the latest owlbot image](#running-locally) against the `golden` directory.

### Lint error

When you modify Python scripts, you may encounter lint errors
Kokoro build:

```
nox > black --check synthtool tests
would reformat synthtool/languages/java.py

Oh no! 💥 💔 💥
1 file would be reformatted, 78 files would be left unchanged.
```

In this case, install [nox](https://nox.thea.codes/en/stable/) and run
`nox -s lint` to reproduce the lint problems and `black synthtool` applies
the suggested formatting.

