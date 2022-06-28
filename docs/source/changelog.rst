Changelog
=========

Versions follow the `Semantic Versioning 2.0.0 <https://semver.org/>`_
standard.

.. Entry title format: django-overcomingbias-api 1.2.3 (release date)

.. Entry items:
.. Breaking Changes = backward-incompatible changes
.. Deprecations = functionality marked as deprecated
.. Features = Added new features
.. Improvements = Improvements to existing features
.. Bug Fixes
.. Improved Documentation
.. Trivial/Internal Changes

django-overcomingbias-api 0.2.5 (2022-06-28)
--------------------------------------------

Bug fixes
^^^^^^^^^

- Truncate ``ExternalLink`` ``url``s to their maximum allowed length (2048). Avoids bug
  with post 2019/04/identity-norms.


django-overcomingbias-api 0.2.4 (2022-06-28)
--------------------------------------------

Bug fixes
^^^^^^^^^

- Increased the ``max_length`` of various ``ContentItem`` fields to match their actual
  maximum lengths.

django-overcomingbias-api 0.2.3 (2022-06-28)
--------------------------------------------

Improvements
^^^^^^^^^^^^

- If an error occurs during downloading new posts, it is now possible to resume
  "pulling" posts without having to reset the database.

Bug fixes
^^^^^^^^^

- Increased the ``max_length`` of the ``ExternalLink`` ``url``s to 2048 (from the
  Django default of 200). Solves errors when trying to store long URLs.

django-overcomingbias-api 0.2.2 (2022-06-27)
--------------------------------------------

Improvements
^^^^^^^^^^^^

- Download overcomingbias posts in chunks by default to reduce memory usage.
  Chunk size is controlled by the ``OBAPI_DOWNLOAD_BATCH_SIZE`` setting.


django-overcomingbias-api 0.2.0 (2022-05-30)
--------------------------------------------

Features
^^^^^^^^

- Ability to export sequences of posts using pandoc.

Improvements
^^^^^^^^^^^^

- Preprocessing of HTML content from overcomingbias posts

- Refactored ModelAdmin classes (to allow for asynchronous execution of some actions)

Bug fixes
^^^^^^^^^

- Various bug fixes

django-overcomingbias-api 0.1.0 (2022-04-13)
--------------------------------------------

Initial release.

See docs at `<https://django-overcomingbias-api.readthedocs.io/en/stable/>`_.
