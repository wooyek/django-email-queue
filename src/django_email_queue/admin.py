# coding=utf-8
# Copyright (c) 2016 Janusz Skonieczny

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from . import models


@admin.register(models.QueuedEmailMessage)
class QueuedEmailMessageAdmin(admin.ModelAdmin):
    list_display = (
        'created',
        'posted',
        'subject',
        'to',
        'cc',
        'bcc',
    )
    list_filter = ('status', 'from_email')
    date_hierarchy = 'created'
    actions = ['bulk_send']
    search_fields = ('to', 'subject', 'cc', 'bcc')
    readonly_fields = ('created', 'ts')

    # noinspection PyUnusedLocal
    def bulk_send(self, request, queryset):
        models.QueuedEmailMessage.bulk_send(queryset)

    bulk_send.short_description = _("bulk send")
