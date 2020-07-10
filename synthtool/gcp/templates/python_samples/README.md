[//]: # "This README.md file is auto-generated, all changes to this file will be lost."
[//]: # "To regenerate it, use `python -m synthtool`."

## Python Sample Folder for {{ metadata['repo']['name_pretty'] }} 

This directory contains samples for {{ metadata['repo']['name_pretty'] }}.

## Getting Started
-------------------------------------------------------------------------------

### Prerequisites
See the [Authentication Getting Started Guide][authentication]. Contribution guidelines, the language style guide, and license information can be found in the base parent directiory.{% if metadata['repo']['requires_billing'] %}You will need to [enable billing][enable_billing] to use Google {{ metadata['repo']['name_pretty'] }}.{% endif %}
{% if metadata['repo']['custom_content'] is defined %}{{ metadata['repo']['custom_content']}}{% endif %}
If this is your first time working with GCP products, you will need to set up a project. *For more information on basic setup, view the information in the parent directory's README.*

### Install Dependencies

1. Check to make sure you have `pip` installed and have created a `virtualenv`.

1. Clone the sample folder and navigate to the sample directory you want to use.

1. Install the dependencies needed to run the samples.

```bash
    $ pip install -r requirements.txt
```

## Samples
-------------------------------------------------------------------------------
{% if metadata['repo']['samples']|length %}
Samples, quickstarts, and other documentation available for this product is available at <a href="{{ metadata['repo']['product_documentation'] }}">the product documentation.</a>.

{% for sample in range(metadata['repo']['samples']|length) %}
### {{ metadata['repo']['samples'][sample]['name']}}
-------------------------------------------------------------------------------

<a href="https://console.cloud.google.com/cloudshell/open?git_repo=https://github.com/{{ metadata['repo']['repo'] }}&page=editor&open_in_editor={{ metadata['repo']['samples'][sample]['file'] }}">
         <img alt="Open in Cloud Shell" src="http://gstatic.com/cloudssh/images/open-btn.png">
</a>

{{ metadata['repo']['samples'][sample]['description']}}

To run this sample:

```bash
    $ python {{ metadata['repo']['samples'][sample]['file']}}
```
{% if metadata['repo']['samples'][sample]['custom_content'] is defined %}{{ metadata['repo']['samples'][sample]['custom_content'] }}{% endif %}{% endfor %}{% endif %}

## Additional Information
-------------------------------------------------------------------------------
{% if metadata['repo']|length %}{% if metadata['repo']['cloud_client_library'] %}
This sample uses the [Google Cloud Client Library for Python][client_library_python].
You can read the documentation for more details on API usage and use GitHub
to [browse the source][source] and  [report issues][issues].{% endif %}
For [contributing guidelines][contrib_guide], the [Python style guide][py_style], and more information on prerequisite steps, view
the product source code at <a href="https://github.com/{{ metadata['repo']['repo'] }}">{{ metadata['repo']['repo'] }}</a>.
{% endif %}

[authentication]: https://cloud.google.com/docs/authentication/getting-started
[enable_billing]:https://cloud.google.com/apis/docs/getting-started#enabling_billing
[client_library_python]: https://googlecloudplatform.github.io/google-cloud-python/
[source]: https://github.com/GoogleCloudPlatform/google-cloud-python
[issues]: https://github.com/GoogleCloudPlatform/google-cloud-python/issues
[contrib_guide]: https://github.com/googleapis/google-cloud-python/blob/master/CONTRIBUTING.rst
[py_style]: http://google.github.io/styleguide/pyguide.html