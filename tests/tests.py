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
import os
from datetime import date, datetime, timedelta

import six
from django.conf import settings
from django.contrib import admin
from django.core.mail import EmailMultiAlternatives
from django.core.mail import send_mail
from django.core.management import call_command, execute_from_command_line
from mock import patch, MagicMock

from django.test import TestCase

from django_email_queue import models, backends
from django_email_queue.admin import QueuedEmailMessageAdmin
from django_email_queue.models import QueuedEmailMessage, QueuedEmailMessageStatus
from tests.factory import QueuedEmailMessageFactory


class BackendsTests(TestCase):
    @patch("django_email_queue.backends.EmailBackend.send_messages")
    def test_send_mail(self, send_messages):
        self.assertEqual(os.environ.get('DJANGO_SETTINGS_MODULE'), 'tests.test_settings')
        self.assertEqual("django_email_queue.backends.EmailBackend", settings.EMAIL_BACKEND)
        send_mail("foo", "bar", "me@examle.com", ["to@example.com"])
        self.assertTrue(send_messages.called)

    @patch("django_email_queue.models.QueuedEmailMessage._create")
    def test_send_mail2(self, create):
        send_mail("foo", "bar", "me@examle.com", ["to@example.com"])
        self.assertTrue(create.called)

    @patch("django_email_queue.models.QueuedEmailMessage.queue")
    def test_send_messages(self, queue):
        message = EmailMultiAlternatives()
        backends.EmailBackend().send_messages([message])
        queue.assert_called_with([message])

    @patch("django_email_queue.models.QueuedEmailMessage.send")
    def test_send_messages(self, send):
        with self.settings(EMAIL_QUEUE_EAGER=True):
            message = EmailMultiAlternatives(to=["to@example.com"])
            backends.EmailBackend().send_messages([message])
            self.assertTrue(send.called)

    @patch("django.core.mail.backends.console.EmailBackend.send_messages")
    def test_eager(self, send_messages):
        with self.settings(EMAIL_QUEUE_EAGER=True):
            send_mail("foo", "bar", "me@examle.com", ["to@example.com"])
            self.assertTrue(send_messages.called)

class QueuedEmailMessageTests(TestCase):
    @patch("django.core.mail.backends.console.EmailBackend.send_messages")
    def test_no_recipiends(self, send_messages):
        message = models.QueuedEmailMessage()
        message.send()
        self.assertFalse(send_messages.called)
        self.assertIsNotNone(message.pk)
        self.assertIsNotNone(message.posted)
        self.assertEqual(models.QueuedEmailMessageStatus.posted, message.status)

    @patch("django.core.mail.backends.console.EmailBackend.send_messages")
    def test_send(self, send_messages):
        mail = models.QueuedEmailMessage(to="to@example.com", body_html="some html").send()
        self.assertTrue(send_messages.called)
        self.assertEqual(1, len(mail.alternatives))
        self.assertEqual("some html", mail.alternatives[0][0])
        self.assertEqual("text/html", mail.alternatives[0][1])

    @patch("django_email_queue.models.QueuedEmailMessage.send")
    def test_send_queued_limit(self, send):
        QueuedEmailMessageFactory.create_batch(5)
        QueuedEmailMessage.send_queued(3)
        self.assertEqual(3, send.call_count)

    @patch("django_email_queue.models.QueuedEmailMessage.send")
    def test_send_queued(self, send):
        QueuedEmailMessageFactory.create_batch(11, status=QueuedEmailMessageStatus.posted)
        QueuedEmailMessageFactory.create_batch(5)
        QueuedEmailMessage.send_queued()
        self.assertEqual(5, send.call_count)

    def test_queue(self):
        email_message = EmailMultiAlternatives(
            "foo", "bar", "me@example.com", ["to@exmaple.com", "to2@exmaple.com"], ["bcc@example.com", "bcc2@example.com"],
            cc=["cc@example.com", "cc2@example.com"], reply_to=["no-reply@example.com", "no-reply2@example.com"]
        )
        email_message.attach_alternative("baz", "text/html")
        instance = list(QueuedEmailMessage.queue([email_message]))[0]
        self.assertIsNotNone(instance.pk)
        self.assertIsNotNone(instance.created)
        self.assertEqual(QueuedEmailMessageStatus.created, instance.status)
        self.assertEqual("foo", instance.subject)
        self.assertEqual("bar", instance.body_text)
        self.assertEqual("baz", instance.body_html)
        self.assertEqual("me@example.com", instance.from_email)
        self.assertEqual("to@exmaple.com, to2@exmaple.com", instance.to)
        self.assertEqual("cc@example.com, cc2@example.com", instance.cc)
        self.assertEqual("bcc@example.com, bcc2@example.com", instance.bcc)
        self.assertEqual("no-reply@example.com, no-reply2@example.com", instance.reply_to)

    def test_not_supported_alternatives(self):
        email_message = EmailMultiAlternatives("foo", "bar", "from@example.com", ["to@example.com"])
        email_message.attach_alternative("some", "text/json")
        generator = QueuedEmailMessage.queue([email_message])
        self.assertRaises(NotImplementedError, list, generator)

    def test_no_recipients(self):
        email_message = EmailMultiAlternatives("foo", "bar", "from@example.com")
        email_message.attach_alternative("some", "text/json")
        generator = QueuedEmailMessage.queue([email_message])
        self.assertRaises(AssertionError, list, generator)

    def test_str(self):
        o = QueuedEmailMessage(subject="ążśźćńółĄŻŚŹĘĆŃÓŁ", to="b")
        self.assertEqual(u"QueuedEmailMessage:ążśźćńółĄŻŚŹĘĆŃÓŁ:b", six.text_type(o))


class QueuedEmailMessageStatusTests(TestCase):
    def test_values(self):
        self.assertEqual([0, 1], QueuedEmailMessageStatus.values())


class CommandTests(TestCase):
    @patch("django_email_queue.models.QueuedEmailMessage.send_queued")
    def test_command(self, send_queued):
        execute_from_command_line(argv=["", "send_queued_messages"])
        self.assertTrue(send_queued.called)


class TestAdmin(TestCase):
    def test_admin(self):
        admin.autodiscover()

    @patch("django_email_queue.models.QueuedEmailMessage.bulk_send")
    def test_send(self, bulk_send):
        qry = QueuedEmailMessage.objects.all()
        QueuedEmailMessageAdmin(QueuedEmailMessage, None).bulk_send(None, qry)
        self.assertTrue(bulk_send.called)

    def test_checks(self):
        from django.core.management import BaseCommand
        BaseCommand().check(display_num_errors=True)

class TestWorker(TestCase):
    def test_worker(self):
        from django_email_queue import worker