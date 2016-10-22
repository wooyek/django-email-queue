#!/usr/bin/env python
import logging
import os
import sys


logging.basicConfig(format='%(asctime)s %(levelname)-7s %(thread)-5d %(filename)s:%(lineno)s | %(funcName)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logging.getLogger().setLevel(logging.DEBUG)
logging.disable(logging.NOTSET)

logging.debug("Importing: %s" % __file__)

from pathlib import Path
SRC_PATH = str(Path(__file__).parent / 'src')


def filter_deprecation_warnings(record):
    warnings_to_suppress = [
        'RemovedInDjango110Warning'
    ]
    msg = record.getMessage()
    return not any([warn in msg
                    for warn in warnings_to_suppress
                    if not msg.startswith(SRC_PATH)])

logging.getLogger('py.warnings').addFilter(filter_deprecation_warnings)


if __name__ == "__main__":
    if SRC_PATH not in sys.path:
        sys.path.append(SRC_PATH)
    assert(os.environ.get('DJANGO_SETTINGS_MODULE') == 'tests.test_settings')
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.test_settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
