==================
Django email queue
==================

Queening and storing EMAIL_BACKEND for django.


.. image:: https://img.shields.io/pypi/v/django-email-queue.svg
        :target: https://pypi.python.org/pypi/django-email-queue

.. image:: https://img.shields.io/travis/wooyek/django-email-queue.svg
        :target: https://travis-ci.org/wooyek/django-email-queue

.. image:: https://readthedocs.org/projects/django-email-queue/badge/?version=latest
        :target: https://django-email-queue.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status
.. image:: https://coveralls.io/repos/github/wooyek/django-email-queue/badge.svg?branch=develop
        :target: https://coveralls.io/github/wooyek/django-email-queue?branch=develop
        :alt: Coveralls.io coverage

.. image:: https://codecov.io/gh/wooyek/django-email-queue/branch/develop/graph/badge.svg
        :target: https://codecov.io/gh/wooyek/django-email-queue
        :alt: CodeCov coverage

.. image:: https://api.codeclimate.com/v1/badges/0e7992f6259bc7fd1a1a/maintainability
        :target: https://codeclimate.com/github/wooyek/django-email-queue/maintainability
        :alt: Maintainability

.. image:: https://img.shields.io/github/license/wooyek/django-email-queue.svg
        :target: https://github.com/wooyek/django-email-queue/blob/develop/LICENSE
        :alt: License

.. image:: https://img.shields.io/twitter/url/https/github.com/wooyek/django-email-queue.svg?style=social
        :target: https://twitter.com/intent/tweet?text=Wow:&url=https://github.com/wooyek/django-email-queue
        :alt: Tweet about this project

.. image:: https://img.shields.io/badge/Say%20Thanks-!-1EAEDB.svg
        :target: https://saythanks.io/to/wooyek


* Free software: GNU Affero General Public License v3
* Documentation: https://django-email-queue.readthedocs.io.

No change in django send_messages usage to get message storing
--------------------------------------------------------------

You don't have to change the way you send messages, this app will plugin into the usual django plumbing.

This way all the email send though django EMAIL_BACKEND will get stored for auditing.


No overhead infrastructure
--------------------------

You don't have to setup overhead infrastructure (e.g. celery, redis and rabbitmq) just to send emails
asynchronously. You can use a simple worker that will send queued emails.

When you get big and having a MQ and all that is a good choice, all you have to to is set
EMAIL_QUEUE_EMAIL_BACKEND to 'djcelery_email.backends.CeleryEmailBackend'.
This way you get message storing for auditing and will use pro setup for asynchronously ran tasks.

Quickstart
----------


Install Django email queue::

    pip install django-email-queue

This is a plugin replacement for your current EMAIL_BACKEND. You'll still use it to send actual messages,
but before them they'll get stored and queued in models visible from admin panel.

.. code:: python

    EMAIL_BACKEND = 'django_email_queue.backends.EmailBackend'
    EMAIL_QUEUE_EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

    INSTALLED_APPS = [
        ...
        'django_email_queue.apps.DjangoEmailQueueConfig',
    ]

You'll be able to send them and clear the queue through from a management command for example using cron jobs.



Running Tests
-------------

Does the code actually work?

::

    $ pipenv install --dev
    $ pipenv shell
    $ tox


We recommend using pipenv_ but a legacy approach to creating virtualenv and installing requirements should also work.
Please install `requirements/development.txt` to setup virtual env for testing and development.


Credits
-------

This package was created with Cookiecutter_ and the `wooyek/cookiecutter-django-app`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`wooyek/cookiecutter-django-app`: https://github.com/wooyek/cookiecutter-django-app
.. _`pipenv`: https://docs.pipenv.org/install
