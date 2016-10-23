# coding=utf-8
# Copyright (c) 2016 Janusz Skonieczny
from django.test.runner import DiscoverRunner


class ForceEmailBackendRunner(DiscoverRunner):
    def setup_test_environment(self, **kwargs):
        super(ForceEmailBackendRunner, self).setup_test_environment(**kwargs)
        # setup_test_environment() will override an EMAIL_BACKEND setting
        # we need to revert that change and allow test settings to set it as it pleasess
        from django.conf import settings
        from django.core import mail
        # noinspection PyUnresolvedReferences,PyProtectedMember
        settings.EMAIL_BACKEND = mail._original_email_backend
