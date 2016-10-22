# coding=utf-8
from django.core.mail.backends.base import BaseEmailBackend

from django_email_queue.models import QueuedEmailMessage


class EmailBackend(BaseEmailBackend):
    def send_messages(self, email_messages):
        QueuedEmailMessage.queue(email_messages)