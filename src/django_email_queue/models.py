# coding=utf-8
# Copyright (c) 2016 Janusz Skonieczny

from __future__ import absolute_import, unicode_literals

import logging
from datetime import timedelta
from enum import IntEnum

import six
from django.conf import settings
from django.core.mail.message import EmailMultiAlternatives
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class ChoicesIntEnum(IntEnum):
    """Extends IntEum with django choices generation capability"""

    @classmethod
    def choices(cls):
        return [(item.value, _(item.name.replace("_", " ").capitalize())) for item in cls]

    @classmethod
    def values(cls):
        return [item.value for item in cls]


class QueuedEmailMessageStatus(ChoicesIntEnum):
    created = 0
    posted = 1
    sending = 2
    discarded = 3


HTML_MIME_TYPE = 'text/html'
EMAIL_ADDRESS_SEPARATOR = ', '


@six.python_2_unicode_compatible
class QueuedEmailMessage(models.Model):
    status = models.PositiveSmallIntegerField(choices=QueuedEmailMessageStatus.choices(), default=QueuedEmailMessageStatus.created)
    created = models.DateTimeField(auto_now_add=True)
    posted = models.DateTimeField(blank=True, null=True)
    ts = models.DateTimeField(blank=True, null=True, auto_now=True)
    encoding = models.CharField(max_length=15, blank=True, null=True)
    from_email = models.CharField(max_length=300)
    to = models.TextField(blank=True, null=True)
    cc = models.TextField(blank=True, null=True)
    bcc = models.TextField(blank=True, null=True)
    reply_to = models.TextField(blank=True, null=True)
    subject = models.CharField(max_length=300)
    body_text = models.TextField()
    body_html = models.TextField(blank=True, null=True)

    # TODO: attachments, headers, alternatives

    def __str__(self):
        return u"{}:{}:{}:{}".format(self.__class__.__name__, self.pk, self.subject, self.to)

    @classmethod
    def _create(cls, email_message, commit=True):
        """A factory method creates model from a base django EmailMultiAlternatives instance."""
        assert email_message.recipients()

        instance = cls()
        instance.encoding = email_message.encoding or settings.DEFAULT_CHARSET
        instance.from_email = email_message.from_email
        instance.to = EMAIL_ADDRESS_SEPARATOR.join(email_message.to)
        instance.cc = EMAIL_ADDRESS_SEPARATOR.join(email_message.cc)
        instance.bcc = EMAIL_ADDRESS_SEPARATOR.join(email_message.bcc)
        instance.reply_to = EMAIL_ADDRESS_SEPARATOR.join(email_message.reply_to)
        instance.subject = email_message.subject
        instance.body_text = email_message.body

        for content, mime_type in email_message.alternatives:
            if mime_type != HTML_MIME_TYPE:
                msg = "Only '{}' mime type is supported, can not send a message with {} alternative"
                msg.format(HTML_MIME_TYPE, mime_type)
                raise NotImplementedError(msg)
            instance.body_html = content

        if commit:
            instance.save()

        return instance

    @classmethod
    def queue(cls, email_messages):
        for item in email_messages:
            instance = cls._create(item)
            logging.debug("Queue message: %s", instance)
            yield instance

    def send(self, connection=None, fail_silently=True):
        if self.created:
            age_hours = (timezone.now() - self.created).total_seconds() / 3600
            if settings.EMAIL_QUEUE_DISCARD_HOURS and age_hours > settings.EMAIL_QUEUE_DISCARD_HOURS:
                self.status = QueuedEmailMessageStatus.discarded
                self.save()
                return
        try:
            return self._send(connection=connection, fail_silently=False)
        except Exception as ex:
            if fail_silently is False:
                raise ex
            # Log error but do not block other messages
            logging.error("Email send failed: {}".format(self), exc_info=ex)

    def _send(self, connection=None, fail_silently=False):
        if connection is None:
            from django.core.mail import get_connection
            connection = get_connection(
                backend=settings.EMAIL_QUEUE_EMAIL_BACKEND,
                fail_silently=fail_silently
            )

        to = self.to.split(EMAIL_ADDRESS_SEPARATOR) if self.to and self.to.strip() else None
        cc = self.cc.split(EMAIL_ADDRESS_SEPARATOR) if self.cc and self.cc.strip() else None
        bcc = self.bcc.split(EMAIL_ADDRESS_SEPARATOR) if self.bcc and self.bcc.strip() else None

        mail = EmailMultiAlternatives(
            subject=self.subject,
            body=self.body_text,
            from_email=self.from_email,
            to=to,
            cc=cc,
            bcc=bcc,
            connection=connection
        )
        if self.body_html:
            mail.attach_alternative(self.body_html, HTML_MIME_TYPE)

        self.status = QueuedEmailMessageStatus.sending
        self.save()
        mail.send(fail_silently=fail_silently)
        self.posted = timezone.now()
        self.status = QueuedEmailMessageStatus.posted
        self.save()
        logging.debug("Message posted: %s", self)
        return mail

    @classmethod
    def send_queued(cls, limit=None):
        seconds = settings.EMAIL_QUEUE_RETRY_SECONDS
        retry = timezone.now() - timedelta(seconds=seconds)
        qry = cls.objects.filter(
            Q(status=QueuedEmailMessageStatus.created) |
            Q(status=QueuedEmailMessageStatus.sending, ts__lte=retry)
        ).order_by("created")
        if limit:
            qry = qry[:limit]
        cls.bulk_send(qry)

    @classmethod
    def bulk_send(cls, qry):
        for message in qry:
            message.send()
