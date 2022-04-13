django-overcomingbias-api: an API to Robin Hanson's content
===========================================================

``django-overcomingbias-api`` is a standalone `Django <https://www.djangoproject.com/>`_
app which lets you create and manage an API to (some of) Robin Hanson's content.

It scrapes the `overcomingbias <https://www.overcomingbias.com/>`_ blog (and other
sites) and presents the data in a structured form via
`REST <https://en.wikipedia.org/wiki/Representational_state_transfer>`_ and
`GraphQL <https://graphql.org/>`_ APIs.

Basic Usage
-----------

A graphical user interface is provided through the
`Django admin site <https://docs.djangoproject.com/en/dev/ref/contrib/admin/>`_.

To initialise a database of all overcomingbias posts, use the "pull" button:

.. image:: https://raw.githubusercontent.com/chris-mcdo/django-overcomingbias-api/main/docs/source/_static/pull-and-sync.png
   :align: center
   :alt: Create and update overcomingbias posts from the admin site

Add new posts with "pull", and update modified posts with "sync".
(You can also add content from YouTube and Spotify.)

Categorise content according to the "ideas" and "topics" it contains, or by generic
"tags".
Use the admin site and custom
`Admin Actions <https://docs.djangoproject.com/en/dev/ref/contrib/admin/actions/>`_
to manage content.

*Coming soon* Link the app in your URL config to access the REST or GraphQL APIs:

.. code-block:: python

    # urls.py

    urlpatterns = [
        ...
        path("", include("obapi.urls")),
        ...
    ]

..  Example of using GraphQL / REST API

Alternatively, provide your own views for each post:

.. code-block:: python

    # urls.py
    from django.urls import path, register_converter
    from obapi.converters import OBPostNameConverter
    from myapp.views import ob_detail_view

    register_converter(OBPostNameConverter, "ob_name")
    urlpatterns = [
        ...
        path(
            "content/overcomingbias/<ob_name:item_id>",
            ob_detail_view, # custom view
            name="obcontentitem_detail",
        ),
        ...
    ]

Features
--------

Currently, content can be scraped from the following sources:

- The `overcomingbias <https://www.overcomingbias.com/>`_ blog (added automatically)

- YouTube videos (add videos manually using their URLs)

- Spotify podcast episodes (add episodes manually using their URLs)

Documentation
-------------

Read the full documentation `here <https://django-overcomingbias-api.readthedocs.io/en/stable/>`_,
including the `Installation and Getting Started Guide
<https://django-overcomingbias-api.readthedocs.io/en/stable/getting-started.html>`_.


Bugs/Requests
-------------

Please use the
`GitHub issue tracker <https://github.com/chris-mcdo/django-overcomingbias-api/issues>`_
to submit bugs or request features.

Changelog
---------

See the
`Changelog <https://django-overcomingbias-api.readthedocs.io/en/stable/changelog.html>`_
for a list of fixes and enhancements at each version.

License
-------

Copyright (c) 2022 Christopher McDonald

Distributed under the terms of the
`MIT <https://github.com/chris-mcdo/django-overcomingbias-api/blob/main/LICENSE>`_
license.

All overcomingbias posts are copyright the original authors.
