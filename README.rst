=============================
Django Policies
=============================

.. .. image:: https://badge.fury.io/py/django-policies.svg
..     :target: https://badge.fury.io/py/django-policies

.. image:: https://travis-ci.org/fedenko/django-policies.svg?branch=main
    :target: https://travis-ci.org/fedenko/django-policies

.. image:: https://codecov.io/gh/fedenko/django-policies/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/fedenko/django-policies

Policies on top of standard django permissions.

Documentation
-------------

The full documentation is at https://django-policies.readthedocs.io.

Quickstart
----------

Install Django Policies::

    pip install django-policies

Add it to your `INSTALLED_APPS`:

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

Features
--------

* TODO

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ python runtests.py


Development commands
---------------------

::

    pip install -r requirements_dev.txt
    invoke -l


Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
