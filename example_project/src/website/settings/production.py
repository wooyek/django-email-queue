# coding=utf-8
# Created 2014 by Janusz Skonieczny

"""
These heavily rely on staging settings and any modifications should consist only of keys and secrets.
Secrets should be loaded of the environment.

The goal here is to not change any settings may have impact on features present.
Changing keys and secrets should not hava that impact.
"""

import logging
import os
from pathlib import Path

import environ

logging.basicConfig(format='%(asctime)s %(levelname)-7s %(thread)-5d %(filename)s:%(lineno)s | %(funcName)s | %(message)s', datefmt='%H:%M:%S')
logging.getLogger().setLevel(logging.DEBUG)
logging.disable(logging.NOTSET)

logging.debug("Settings loading: %s" % __file__)

name = __name__.split('.')[-1].upper()
print("""
╔═════════════════════════════╗
║ LOADING PRODUCTION SETTINGS ║
╚═════════════════════════════╝
""")

# Set defaults for when env file is not present.
os.environ.update(DEBUG='False', ASSETS_DEBUG='False')

# This will read missing environment variables from a file
# We want to do this before loading any base settings as they may depend on environment
evironment_config = Path(__file__).with_suffix('.env')
if evironment_config.exists():
    environ.Env.read_env(str(evironment_config))

# noinspection PyUnresolvedReferences
from .base import *  # noqa: F402, F403 isort:skip

LOGGING['handlers']['console']['formatter'] = 'heroku'  # noqa: F405
LOGGING['handlers']['file'] = {  # noqa: F405
    'class': 'logging.handlers.RotatingFileHandler',
    'formatter': 'verbose',
    'backupCount': 3,
    'maxBytes': 4194304,  # 4MB
    'level': 'DEBUG',
    'filename': (os.path.join(BASE_DIR, 'logs', 'website.log')),  # noqa: F405
}
LOGGING['root']['handlers'].append('file')  # noqa: F405

log_file = Path(LOGGING['handlers']['file']['filename'])  # noqa: F405
if not log_file.parent.exists():  # pragma: no cover
    logging.info("Creating log directory: {}".format(log_file.parent))
    Path(log_file).parent.mkdir(parents=True)
