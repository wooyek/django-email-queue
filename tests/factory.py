# coding=utf-8
# Copyright (c) 2016 Janusz Skonieczny

from __future__ import absolute_import

import factory

from django_email_queue.models import QueuedEmailMessage


class QueuedEmailMessageFactory(factory.DjangoModelFactory):
    class Meta:
        model = QueuedEmailMessage

    to = factory.Faker('email')
    cc = factory.Faker('email')
    bcc = factory.Faker('email')
    subject = factory.Faker("paragraph", nb_sentences=1)
    body_text = factory.Faker("paragraph", nb_sentences=3)