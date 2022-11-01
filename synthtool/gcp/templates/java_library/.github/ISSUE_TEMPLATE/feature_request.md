---
name: Feature request
about: Suggest an idea for this library

---

{% if metadata['repo']['library_type'] == 'GAPIC_AUTO'
or (metadata['repo']['repo_short'] and metadata['repo']['repo_short'] in ['java-translate', 'java-dns', 'java-notification', 'java-resourcemanager']) %}
:bus: This library has moved to
[google-cloud-java/{{ metadata['repo']['repo_short'] }}](
https://github.com/googleapis/google-cloud-java/tree/main/{{ metadata['repo']['repo_short'] }}).
This repository will be archived in the future.
{% endif %}
**PLEASE READ**: If you have a support contract with Google, please create an issue in the [support console](https://cloud.google.com/support/) instead of filing on GitHub. This will ensure a timely response.

