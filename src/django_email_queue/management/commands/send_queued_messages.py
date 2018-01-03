# coding=utf-8
# Copyright (c) 2016 Janusz Skonieczny
import logging

from django.core.management.base import BaseCommand

from ...models import QueuedEmailMessage


class Command(BaseCommand):
    help = 'Send queued messages'

    def add_arguments(self, parser):
        super(Command, self).add_arguments(parser)
        parser.add_argument(
            "--limit",
            action="store",
            type=int,
            default=10,
            help="Limit the number of emails send. Defaults to 10.",
        )

    def handle(self, *args, **options):
        logging.debug("options: %s" % options)
        QueuedEmailMessage.send_queued(limit=options['limit'])
