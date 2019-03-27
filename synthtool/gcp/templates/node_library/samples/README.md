[//]: # "This README.md file is auto-generated, all changes to this file will be lost."
[//]: # "To regenerate it, use `npm run generate-scaffolding`."
<img src="https://avatars2.githubusercontent.com/u/2810941?v=3&s=96" alt="Google Cloud Platform logo" title="Google Cloud Platform" align="right" height="96" width="96"/>

# [{{ metadata['repo']['name_pretty'] }}: {{ metadata['repo']['language']|language_pretty }} Client](https://github.com/{{ metadata['repo']['repo'] }})

[![Open in Cloud Shell][shell_img]][shell_link]

{{ metadata['partials'] and metadata['partials']['introduction'] }}

## Table of Contents

* [Before you begin](#before-you-begin)
* [Samples](#samples){% if metadata['samples']|length %}{% for sample in metadata['samples'] %}
  * [{{ sample.name }}](#{{ sample.name|slugify }}){% endfor %}{% endif %}

## Before you begin

Before running the samples, make sure you've followed the steps in the
[Using the client library](https://github.com/{{ metadata['repo']['repo']  }}#using-the-client-library) of the client
library's README.

## Samples
{% if metadata['samples']|length %}
{% for sample in metadata['samples'] %}

### {{sample.name}}

View the [source code](https://github.com/{{ metadata['repo']['repo']  }}/blob/master/samples/{{ sample.file }}).

[![Open in Cloud Shell][shell_img]](https://console.cloud.google.com/cloudshell/open?git_repo=https://github.com/{{ metadata['repo']['repo']  }}&page=editor&open_in_editor=samples/{{ sample.file }},samples/README.md)

__Usage:__ 

See available commands:

`node {{ sample.file }} --help`

Run the sample:

`node {{ sample.file }} [command] [options]`

{% if not loop.last %}
-----
{% endif %}

{% endfor %}
{% endif %}

[shell_img]: https://gstatic.com/cloudssh/images/open-btn.png
[shell_link]: https://console.cloud.google.com/cloudshell/open?git_repo=https://github.com/{{ metadata['repo']['repo']  }}&page=editor&open_in_editor=samples/README.md