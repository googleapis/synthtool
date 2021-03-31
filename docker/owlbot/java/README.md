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

This image is built via Cloud Build. From the root of this repository, run:

```bash
gcloud builds submit --config=docker/owlbot/java/cloudbuild.yaml
```
