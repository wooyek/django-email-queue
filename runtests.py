# !/usr/bin/env python
# coding=utf-8
# Copyright (c) 2016 Janusz Skonieczny

import os
import sys

import django
from django.conf import settings
from django.test.utils import get_runner

def runtests(*test_args):
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.test_settings'
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["tests"])
    sys.exit(bool(failures))

if __name__ == "__main__":
    runtests()
