# coding=utf-8

from django.conf import settings

# This is an example
DJANGO_EMAIL_QUEUE_SECRET = settings.SECRET_KEY[::4]
