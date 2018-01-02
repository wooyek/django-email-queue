# -*- coding: utf-8
from __future__ import absolute_import, unicode_literals

from django.conf.urls import include, url

urlpatterns = [
    url(r'^', include('django_email_queue.urls', namespace='django_email_queue')),
]
