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
.. include:: upgrading.rst
{% endif %}
Changelog
---------

For a list of all ``{{ metadata['repo']['distribution_name'] }}`` releases:

.. toctree::
   :maxdepth: 2

   changelog
