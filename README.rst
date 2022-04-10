django-overcomingbias-api: django-overcomingbias-api: an API to Robin Hanson's content
======================================================================================

``django-overcomingbias-api`` is a standalone `Django <https://www.djangoproject.com/>`_
app which creates an API to (some of) Robin Hanson's content.

It scrapes the `overcomingbias <https://www.overcomingbias.com/>`_ blog (and other
sites) and makes this data available via
`REST <https://en.wikipedia.org/wiki/Representational_state_transfer>`_ and
`GraphQL <https://graphql.org/>`_ APIs.

Quick start
-----------

.. Install with pip
    Add to installed apps
    Any necessary patching
    Include URLS
    Migrate
    View in admin site
    Or send it a request

Basic Usage
-----------

.. Main API functions

.. Use of admin site, sync / pull, admin actions

Features
--------

Currently, content can be scraped from the following sources:

- The `overcomingbias <https://www.overcomingbias.com/>`_ blog (added automatically)

- YouTube videos (add videos manually using their URLs)

- Spotify podcast episodes (add episodes manually using their URLs)

Documentation
-------------

.. Where to find docs?
    Getting started guide + full reference

Bugs/Requests
-------------

Please use the
`GitHub issue tracker <https://github.com/chris-mcdo/django-overcomingbias-api/issues>`_
to submit bugs or request features.

Changelog
---------

.. See the
    `Changelog <https://django-overcomingbias-api.readthedocs.io/en/stable/changelog.html>`_
    for a list of fixes and enhancements at each version.

License
-------

Copyright (c) 2022 Christopher McDonald

Distributed under the terms of the
`MIT <https://github.com/chris-mcdo/django-overcomingbias-api/blob/main/LICENSE>`_
license.

All overcomingbias posts are copyright the original authors.
