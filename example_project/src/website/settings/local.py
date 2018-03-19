# coding=utf-8
# Based on https://github.com/wooyek/cookiecutter-django-website by Janusz Skonieczny

import logging
from pathlib import Path

import environ

logging.basicConfig(format='%(asctime)s %(levelname)-7s %(thread)-5d %(filename)s:%(lineno)s | %(funcName)s | %(message)s', datefmt='%H:%M:%S')
logging.getLogger().setLevel(logging.DEBUG)
logging.disable(logging.NOTSET)

logging.debug("Settings loading: %s" % __file__)

# This will read missing environment variables from a file
# We want to do this before loading any base settings as they may depend on environment
environ.Env.read_env(str(Path(__file__).parent / "local.env"), DEBUG='True')
from .base import *  # noqa: F402, F403 isort:skip

# https://docs.djangoproject.com/en/1.6/topics/email/#console-backend
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'
LOGGING['handlers']['mail_admins']['email_backend'] = 'django.core.mail.backends.dummy.EmailBackend'  # noqa: F405

DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
