# coding=utf-8
# Copyright (c) 2016 Janusz Skonieczny

from __future__ import absolute_import, unicode_literals

import os
from datetime import timedelta

import pytest
import six
from django.conf import settings
from django.contrib import admin
from django.core.mail import EmailMultiAlternatives, send_mail
from django.core.management import execute_from_command_line
from django.test import TestCase, override_settings
from django.utils import timezone
from mock import call, patch

from django_email_queue import backends, models
from django_email_queue.admin import QueuedEmailMessageAdmin
from django_email_queue.models import QueuedEmailMessage, QueuedEmailMessageStatus
from tests import factories
from tests.factories import QueuedEmailMessageFactory


class BackendsTests(TestCase):
    @patch("django_email_queue.backends.EmailBackend.send_messages")
    @override_settings(EMAIL_BACKEND='django_email_queue.backends.EmailBackend')
    def test_send_mail(self, send_messages):
        self.assertEqual(os.environ.get('DJANGO_SETTINGS_MODULE'), 'tests.settings')
        self.assertEqual("django_email_queue.backends.EmailBackend", settings.EMAIL_BACKEND)
        send_mail("foo", "bar", "me@examle.com", ["to@example.com"])
        self.assertTrue(send_messages.called)

    @patch("django_email_queue.models.QueuedEmailMessage._create")
    @override_settings(EMAIL_BACKEND='django_email_queue.backends.EmailBackend')
    def test_send_mail2(self, create):
        send_mail("foo", "bar", "me@examle.com", ["to@example.com"])
        self.assertTrue(create.called)

    @patch("django_email_queue.models.QueuedEmailMessage.queue")
    def test_send_messages(self, queue):
        message = EmailMultiAlternatives()
        backends.EmailBackend().send_messages([message])
        queue.assert_called_with([message])

    @patch("django_email_queue.models.QueuedEmailMessage.send")
    def test_send_messages2(self, send):
        with self.settings(EMAIL_QUEUE_EAGER=True):
            message = EmailMultiAlternatives(to=["to@example.com"])
            backends.EmailBackend().send_messages([message])
            self.assertTrue(send.called)

    @patch("django.core.mail.backends.console.EmailBackend.send_messages")
    @override_settings(EMAIL_BACKEND='django_email_queue.backends.EmailBackend')
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
        self.assertEqual(u"QueuedEmailMessage:None:ążśźćńółĄŻŚŹĘĆŃÓŁ:b", six.text_type(o))

    def test_str2(self):
        o = QueuedEmailMessage(subject="ążśźćńółĄŻŚŹĘĆŃÓŁ", to="b", pk=123)
        self.assertEqual(u"QueuedEmailMessage:123:ążśźćńółĄŻŚŹĘĆŃÓŁ:b", six.text_type(o))

    @override_settings(EMAIL_QUEUE_DISCARD_HOURS=2)
    @patch('django_email_queue.models.QueuedEmailMessage._send')
    def test_discard_message(self, send):
        send.side_effect = Exception("Foo")
        item = models.QueuedEmailMessage(created=timezone.now() - timedelta(hours=2, seconds=1))
        item.send()
        self.assertEqual(item.status, models.QueuedEmailMessageStatus.discarded)
        self.assertFalse(send.called)

    @override_settings(EMAIL_QUEUE_DISCARD_HOURS=1)
    @patch('django_email_queue.models.QueuedEmailMessage._send')
    def test_dont_discard_message(self, send):
        send.side_effect = Exception("Foo")
        item = models.QueuedEmailMessage(created=timezone.now() - timedelta(seconds=3599))
        item.send()
        self.assertEqual(models.QueuedEmailMessageStatus.created, item.status)

    @override_settings(EMAIL_QUEUE_DISCARD_HOURS=None)
    @patch('django_email_queue.models.QueuedEmailMessage._send')
    def test_dont_discard_message2(self, send):
        send.side_effect = Exception("Foo")
        item = models.QueuedEmailMessage(created=timezone.now() - timedelta(seconds=3599))
        item.send()
        self.assertEqual(models.QueuedEmailMessageStatus.created, item.status)

    @patch('django_email_queue.models.QueuedEmailMessage._send')
    def test_fail_silently(self, send):
        send.side_effect = Exception("Foo")
        item = models.QueuedEmailMessage(created=timezone.now())
        item.send()

    @patch('django_email_queue.models.QueuedEmailMessage._send')
    def test_dont_fail_silently(self, send):
        send.side_effect = Exception("Foo")
        item = models.QueuedEmailMessage()
        self.assertRaises(Exception, item.send, fail_silently=False)

    @override_settings(EMAIL_QUEUE_RETRY_SECONDS=600)
    @patch('django_email_queue.models.QueuedEmailMessage._send')
    def test_retry_busy(self, send):
        seconds = settings.EMAIL_QUEUE_RETRY_SECONDS + 2
        retry = timezone.now() - timedelta(seconds=seconds)
        message = factories.QueuedEmailMessageFactory(
            ts=retry,
            status=models.QueuedEmailMessageStatus.sending,
        )
        models.QueuedEmailMessage.objects.all().update(ts=retry)
        message.send_queued()
        self.assertTrue(send.called)

    @override_settings(EMAIL_QUEUE_RETRY_SECONDS=600)
    @patch('django_email_queue.models.QueuedEmailMessage._send')
    def test_retry_wait(self, send):
        seconds = settings.EMAIL_QUEUE_RETRY_SECONDS - 2
        retry = timezone.now() - timedelta(seconds=seconds)
        message = factories.QueuedEmailMessageFactory(
            ts=retry,
            status=models.QueuedEmailMessageStatus.sending,
        )
        models.QueuedEmailMessage.objects.all().update(ts=retry)
        message.send_queued()
        self.assertFalse(send.called)


class QueuedEmailMessageStatusTests(TestCase):
    def test_values(self):
        self.assertEqual([0, 1, 2, 3], QueuedEmailMessageStatus.values())


class CommandTests(TestCase):
    @patch("django_email_queue.models.QueuedEmailMessage.send_queued")
    def test_send_command(self, send_queued):
        execute_from_command_line(argv=["", "send_queued_messages"])
        self.assertTrue(send_queued.called)

    @patch("django_email_queue.management.commands.delete_sent_queued_messages.logging")
    def test_delete_command(self, mock_logger):
        QueuedEmailMessageFactory.create_batch(2, status=QueuedEmailMessageStatus.posted)
        QueuedEmailMessageFactory.create_batch(2)
        now = timezone.now()
        QueuedEmailMessage.objects.update(created=now)
        self.assertEqual(2, QueuedEmailMessage.objects.filter(status=QueuedEmailMessageStatus.posted).count())

        execute_from_command_line(argv=["", "delete_sent_queued_messages"])
        mock_logger.debug.assert_has_calls([
            call(u"Deleting queued messages, count: %s, first: %s, last: %s",
                 2, now.isoformat(), now.isoformat()),
            call(u"Queued messages deleted")
        ])
        self.assertEqual(0, QueuedEmailMessage.objects.filter(status=QueuedEmailMessageStatus.posted).count())


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
        pass


@pytest.mark.skipif('DJANGO' not in os.environ, reason="DJANGO env not defined")
def test_django_version():
    # This test testing matrix if django version installed is indeed that requested
    from django import VERSION
    assert "{}.{}".format(VERSION[0], VERSION[1]) == os.environ['DJANGO']
