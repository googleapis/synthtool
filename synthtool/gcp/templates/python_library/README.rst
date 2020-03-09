Python Client for {{ metadata['repo']['name_pretty'] }} API
==============================================

|{{ metadata['repo']['release_level'] }}| |pypi| |versions|

`{{ metadata['repo']['name_pretty'] }} API`_: CHANGE ME: ADD API DESCRIPTION HERE

- `Client Library Documentation`_
- `Product Documentation`_

.. |{{ metadata['repo']['release_level'] }}| image:: 
{%- if metadata['repo']['release_level'] == 'beta' -%} https://img.shields.io/badge/support-beta-orange.svg
{%- elif metadata['repo']['release_level'] == 'alpha' -%} https://img.shields.io/badge/support-alpha-orange.svg
{%- elif metadata['repo']['release_level'] == 'ga' -%} https://img.shields.io/badge/support-ga-gold.svg
{%- endif %}
   :target: 
{%- if metadata['repo']['release_level'] == 'beta' -%} https://github.com/googleapis/google-cloud-python/blob/master/README.rst#beta-support
{%- elif metadata['repo']['release_level'] == 'alpha' -%} https://github.com/googleapis/google-cloud-python/blob/master/README.rst#alpha-support
{%- elif metadata['repo']['release_level'] == 'ga' -%} https://github.com/googleapis/google-cloud-python/blob/master/README.rst#general-availability
{%- endif %}
.. |pypi| image:: https://img.shields.io/pypi/v/{{ metadata['repo']['distribution_name'] }}.svg
   :target: https://pypi.org/project/{{ metadata['repo']['distribution_name'] }}/
.. |versions| image:: https://img.shields.io/pypi/pyversions/{{ metadata['repo']['distribution_name'] }}.svg
   :target: https://pypi.org/project/{{ metadata['repo']['distribution_name'] }}/
.. _{{ metadata['repo']['name_pretty'] }} API: {{ metadata['repo']['product_documentation'] }}
.. _Client Library Documentation: {{ metadata['repo']['client_documentation'] }}
.. _Product Documentation:  {{ metadata['repo']['product_documentation'] }}

Quick Start
-----------

In order to use this library, you first need to go through the following steps:

1. `Select or create a Cloud Platform project.`_
2. `Enable billing for your project.`_
3. `Enable the {{ metadata['repo']['name_pretty'] }} API.`_
4. `Setup Authentication.`_

.. _Select or create a Cloud Platform project.: https://console.cloud.google.com/project
.. _Enable billing for your project.: https://cloud.google.com/billing/docs/how-to/modify-project#enable_billing_for_a_project
.. _Enable the {{ metadata['repo']['name_pretty'] }} API.:  {{ metadata['repo']['product_documentation'] }}
.. _Setup Authentication.: https://googleapis.dev/python/google-api-core/latest/auth.html

Installation
~~~~~~~~~~~~

Install this library in a `virtualenv`_ using pip. `virtualenv`_ is a tool to
create isolated Python environments. The basic problem it addresses is one of
dependencies and versions, and indirectly permissions.

With `virtualenv`_, it's possible to install this library without needing system
install permissions, and without clashing with the installed system
dependencies.

.. _`virtualenv`: https://virtualenv.pypa.io/en/latest/


Mac/Linux
^^^^^^^^^

.. code-block:: console

    pip install virtualenv
    virtualenv <your-env>
    source <your-env>/bin/activate
    <your-env>/bin/pip install {{ metadata['repo']['distribution_name'] }}


Windows
^^^^^^^

.. code-block:: console

    pip install virtualenv
    virtualenv <your-env>
    <your-env>\Scripts\activate
    <your-env>\Scripts\pip.exe install {{ metadata['repo']['distribution_name'] }}

Next Steps
~~~~~~~~~~

-  Read the `Client Library Documentation`_ for {{ metadata['repo']['name_pretty'] }} API
   API to see other available methods on the client.
-  Read the `{{ metadata['repo']['name_pretty'] }} API Product documentation`_ to learn
   more about the product and see How-to Guides.
-  View this `repository’s main README`_ to see the full list of Cloud
   APIs that we cover.

.. _{{ metadata['repo']['name_pretty'] }} API Product documentation:  {{ metadata['repo']['product_documentation'] }}
.. _repository’s main README: https://github.com/googleapis/google-cloud-python/blob/master/README.rst