# coding=utf-8
# Copyright (c) 2016 Janusz Skonieczny
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import absolute_import
from __future__ import unicode_literals

import logging
from enum import IntEnum

import six
from django.core.mail.message import EmailMultiAlternatives
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from .conf import settings


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


HTML_MIME_TYPE = 'text/html'
EMAIL_ADDRESS_SEPARATOR = ', '


@six.python_2_unicode_compatible
class QueuedEmailMessage(models.Model):
    status = models.PositiveSmallIntegerField(choices=QueuedEmailMessageStatus.choices(), default=QueuedEmailMessageStatus.created)
    created = models.DateTimeField(auto_now_add=True)
    posted = models.DateTimeField(blank=True, null=True)
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
        return u"{}:{}:{}".format(self.__class__.__name__, self.subject, self.to)

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

    def send(self, connection=None, fail_silently=False):
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

        mail.send(fail_silently=fail_silently)
        self.posted = timezone.now()
        self.status = QueuedEmailMessageStatus.posted
        self.save()
        logging.debug("Message posted: %s", self)
        return mail

    @classmethod
    def send_queued(cls, limit=None):
        qry = cls.objects.filter(status=QueuedEmailMessageStatus.created).order_by("created")
        if limit:
            qry = qry[:limit]
        cls.bulk_send(qry)

    @classmethod
    def bulk_send(cls, qry):
        for message in qry:
            message.send()
