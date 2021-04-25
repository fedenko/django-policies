=====
Usage
=====

To use Django Policies in a project, add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'django_policies.apps.PoliciesConfig',
        ...
    )

Add Django Policies's URL patterns:

.. code-block:: python

    from django_policies import urls as django_policies_urls


    urlpatterns = [
        ...
        url(r'^', include(django_policies_urls)),
        ...
    ]
