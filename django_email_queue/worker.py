# coding=utf-8
# Copyright (c) 2016 Janusz Skonieczny

from __future__ import absolute_import

import getpass
import logging
import os

import sys
from time import sleep

logging.basicConfig(format='%(asctime)s %(levelname)-7s %(thread)-5d %(filename)s:%(lineno)s | %(funcName)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logging.getLogger().setLevel(logging.DEBUG)
logging.disable(logging.NOTSET)

# logging.info("Current user: %s" % getpass.getuser())

assert 'DJANGO_SETTINGS_MODULE' in os.environ, "DJANGO_SETTINGS_MODULE is missing from environment, you must set if before running this worker"
logging.info("os.environ['DJANGO_SETTINGS_MODULE']: %s" % os.environ['DJANGO_SETTINGS_MODULE'])

cwd = os.getcwd()

if cwd not in sys.path:  # pragma: no cover
    sys.path.append(cwd)

# Show a debugging info on console
logging.debug("__file__ = %s", __file__)
logging.debug("sys.version = %s", sys.version)
logging.debug("os.getpid() = %s", os.getpid())
logging.debug("os.getcwd() = %s", cwd)
logging.debug("os.curdir = %s", os.curdir)
logging.debug("sys.path:\n\t%s", "\n\t".join(sys.path))
logging.debug("PYTHONPATH:\n\t%s", "\n\t".join(os.environ.get('PYTHONPATH', "").split(';')))
logging.debug("sys.modules.keys() = %s", repr(sys.modules.keys()))
logging.debug("sys.modules.has_key('website') = %s", 'website' in sys.modules)

from django.conf import settings
import django

django.setup()
logging.debug("settings.__dir__: %s", settings.__dir__())
logging.debug("settings.DEBUG: %s", settings.DEBUG)


def run():  # pragma: no cover
    from django_email_queue.models import QueuedEmailMessage

    while True:
        QueuedEmailMessage.send_queued(10)
        seconds = settings.EMAIL_QUEUE_SLEEP_TIME
        logging.debug("Will sleep for %s seconds", seconds)
        sleep(seconds)


if __name__ == '__main__':  # pragma: no cover
    run()
