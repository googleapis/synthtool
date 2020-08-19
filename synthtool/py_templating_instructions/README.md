# Using Synthtool for Python Samples

Synthtool supports template files using [Jinja](http://jinja.pocoo.org/).

Templates used for the Python samples are found in subdirectories of [`synthtool/gcp/templates/python_samples`](gcp/templates/python_samples)

To use Synthtool for Python samples you will need to create or update two files in the root directory of the product folder to which the samples belong.

- Templates are generated using `gcp.CommonTemplates.py_samples()` in a `synth.py` file.

- You can provide variables to templates as keyword arguments, there are multiple methods of providing kwargs to Synthtool but Python samples currently use **metadata files** called `.repo-metadata.json`

This folder provides a bare-bones version of a `synth.py` file, which you can either copy directly into your repository or add the generation lines of code to your repo's existing `synth.py` file.

It also contains a sample version of a `.repo-metadata.json` file which you can also copy and fill in with your samples' information, or use as a reference additions to your repo's existing file.

## Synth file

Either append this code into your existing synth.py file, or copy it into the repo. No changes are required, but the source for the function being called is at `gcp.CommonTemplates.py_samples()` .

## Metadata

Lines 1-12 contain information about the client library, and likely already exist if your client library uses Synthtool already.

`samples` is an array, where each element is a list of sample information. The key options are:
- `name` : Sample name
- `description` : Description of the sample
- `file` : The main file associated with this sample
- `runnable` (Optional) : Either True/False, depending on whether this sample is made to be run by running the above file name, or not.
- `custom_content` (Optional) : This is custom content that appears after all other information generated about the sample
- `override_path` (Optional): If you would like to have a seperate README generate for this file in a different folder within the directory that holds the samples, ex. a folder named `quickstart`, specify that relative path here.
If multiple samples have the same override path, the README in that folder will contain info for all those samples.
