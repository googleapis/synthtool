.. include:: README.rst

.. include:: multiprocessing.rst
{% if versions|length > 1 %}
This package includes clients for multiple versions of {{ metadata['repo']['name_pretty'] }}.
By default, you will get version ``{{ versions | first }}``.
{% endif %}
{% for version in versions %}
API Reference
-------------
.. toctree::
    :maxdepth: 2

    {{ version }}/services
    {{ version }}/types
{% endfor %}
{% if include_uprading_doc %}
Migration Guide
---------------

See the guide below for instructions on migrating to the latest version.

.. toctree::
    :maxdepth: 2

    UPGRADING

{% endif %}
Changelog
---------

For a list of all ``{{ metadata['repo']['distribution_name'] }}`` releases:

.. toctree::
    :maxdepth: 2

    changelog
