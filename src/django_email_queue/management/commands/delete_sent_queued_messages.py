# -*- coding: utf-8 -*-

import logging

from django.core.management.base import BaseCommand

from django_email_queue.models import QueuedEmailMessage, QueuedEmailMessageStatus


class Command(BaseCommand):
    help = 'Delete sent queued messages'

    def handle(self, *args, **options):
        sent_qs = QueuedEmailMessage.objects.filter(status=QueuedEmailMessageStatus.posted).order_by('created')
        if not sent_qs.exists():
            logging.debug('No messages to delete')
            return

        logging.debug(
            "Deleting queued messages, count: %s, first: %s, last: %s", sent_qs.count(),
            sent_qs.first().created.isoformat(), sent_qs.last().created.isoformat()
        )
        sent_qs.delete()
        logging.debug('Queued messages deleted')
