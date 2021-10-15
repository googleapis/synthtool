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
{%- if migration_guide_version %}
Migration Guide
---------------

See the guide below for instructions on migrating to the {{ migration_guide_version }} release of this library.

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
