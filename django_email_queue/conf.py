# coding=utf-8
# Copyright (c) 2016 Janusz Skonieczny

# noinspection PyUnresolvedReferences
from django.conf import settings

from appconf import AppConf


class EmailQueueConf(AppConf):
    # The email backend to use. For possible shortcuts see django.core.mail.
    # The default is to use the SMTP backend.
    # Third-party backends can be specified by providing a Python path
    # to a module that defines an EmailBackend class.
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

    # Don't queue messages store them and send them immediately
    # Set this to True if you are going to use
    # `djcelery_email.backends.CeleryEmailBackend` as EMAIL_QUEUE_EMAIL_BACKEND.
    EAGER = False

    # Per minute maximum number of messages to be sent
    # THROTTLE = 30

    # Sleep time between queue checkup
    SLEEP_TIME = 15

    class Meta:
        prefix = 'email_queue'
