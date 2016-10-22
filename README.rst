django-email-queue-backend
==========================

Queening and storing email backed for django.

https://github.com/wooyek/django-email-queue-backend

.. image:: https://img.shields.io/travis/wooyek/django-email-queue-backend.svg
:target: https://travis-ci.org/wooyek/django-pascal-templates

.. image:: https://img.shields.io/coveralls/wooyek/django-email-queue-backend.svg
:target: https://coveralls.io/github/wooyek/django-pascal-templates

.. image:: https://img.shields.io/pypi/v/django-email-queue-backend.svg?maxAge=2592000
:target: https://pypi.python.org/pypi/django-pascal-templates/

.. image:: https://img.shields.io/pypi/dm/django-email-queue-backend.svg?maxAge=2592000
:target: https://pypi.python.org/pypi/django-pascal-templates/

Usage
-----

This is a plugin replacement for your current EMAIL_BACKEND. You'll still use it to send actual messages,
but before them they'll get stored and queued in models visible from admin panel.

You'll be able to send them and clear the queue through from a management command for example using cron jobs.

TODO
----

1. Don't queue, store&send feature. Leaving the queueing tho something more advanced like CeleryEmailBackend.
