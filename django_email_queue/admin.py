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

from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

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
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'is_introduced', 'is_validated', 'is_test_user')
    date_hierarchy = 'created'
    actions = ['bulk_send']

    # noinspection PyUnusedLocal
    @staticmethod
    def bulk_send(request, queryset):
        models.QueuedEmailMessage.bulk_send(queryset)
    bulk_send.short_description = _("bulk send")

