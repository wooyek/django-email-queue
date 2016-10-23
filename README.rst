django-email-queue
==================

Queening and storing EMAIL_BACKEND for django.

https://github.com/wooyek/django-email-queue

.. image:: https://img.shields.io/travis/wooyek/django-email-queue.svg
    :target: https://travis-ci.org/wooyek/django-email-queue

.. image:: https://img.shields.io/coveralls/wooyek/django-email-queue.svg
    :target: https://coveralls.io/github/wooyek/django-email-queue

.. image:: https://img.shields.io/pypi/v/django-email-queue.svg?maxAge=2592000
    :target: https://pypi.python.org/pypi/django-email-queue/

.. image:: https://img.shields.io/pypi/dm/django-email-queue.svg?maxAge=2592000
    :target: https://pypi.python.org/pypi/django-email-queue/

No change in django send_messages usage to get message storing
--------------------------------------------------------------

You don't have to change the way you send messages, this app will plugin into the usual django plumbing.

This way all the email send though django EMAIL_BACKEND will get stored for auditing.


No overhead overhead infrastructure
-----------------------------------

You don't have to setup overhead infrastructure (e.g. celery, redis and rabbitmq) just to send emails
asynchronously. You can use a simple worker that will send queued emails.

When you get big and having a MQ and all that is a good choice, all you have to to is set
EMAIL_QUEUE_EMAIL_BACKEND to 'djcelery_email.backends.CeleryEmailBackend'.
This way you get message storing for auditing and will use pro setup for asynchronously ran tasks.

Usage
-----

This is a plugin replacement for your current EMAIL_BACKEND. You'll still use it to send actual messages,
but before them they'll get stored and queued in models visible from admin panel.

.. code:: python

    EMAIL_BACKEND = 'django_email_queue.backends.EmailBackend'
    EMAIL_QUEUE_EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

    INSTALLED_APPS = [
        ...
        'django_email_queue',
    ]

You'll be able to send them and clear the queue through from a management command for example using cron jobs.

