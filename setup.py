#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

import os
import re
import sys
import uuid
from glob import glob
from os.path import basename, splitext

try:  # for pip >= 10
    # noinspection PyProtectedMember,PyPackageRequirements
    from pip._internal.req.req_file import parse_requirements
except ImportError:  # for pip <= 9.0.3
    # noinspection PyPackageRequirements
    from pip.req import parse_requirements

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')


def requirements(path):
    items = parse_requirements(path, session=uuid.uuid1())
    return [";".join((str(r.req), str(r.markers))) if r.markers else str(r.req) for r in items]


tests_require = requirements(os.path.join(os.path.dirname(__file__), "requirements", "testing.txt"))
install_requires = requirements(os.path.join(os.path.dirname(__file__), "requirements", "production.txt"))


def get_version(*file_paths):
    """Retrieves the version from path"""
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    print("Looking for version in: {}".format(filename))
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


version = get_version("src", "django_email_queue", "__init__.py")


if sys.argv[-1] == 'publish':
    try:
        import wheel
        print("Wheel version: ", wheel.__version__)
    except ImportError:
        print('Wheel library missing. Please run "pip install wheel"')
        sys.exit()
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    sys.exit()

if sys.argv[-1] == 'bump':
    print("Bumping version number:")
    os.system("bumpversion patch --no-tag")
    sys.exit()

if sys.argv[-1] == 'tag':
    print("Tagging the version on git:")
    os.system("git tag -a %s -m 'version %s'" % (version, version))
    os.system("git push --tags")
    sys.exit()

setup(
    name='django-email-queue',
    version=version,
    description="""Queening and storing EMAIL_BACKEND for django.""",
    long_description=readme + '\n\n' + history,
    author="Janusz Skonieczny",
    author_email='js+pypi@bravelabs.pl',
    url='https://github.com/wooyek/django-email-queue',
    packages=find_packages('src', exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    entry_points={
        'console_scripts': [
            # 'django_email_queue=django_email_queue.cli:main'
            'email_queue_worker = django_email_queue.worker:run',
        ]
    },
    include_package_data=True,
    exclude_package_data={
        '': ['test*.py', 'tests/*.env', '**/tests.py'],
    },
    python_requires='>=2.7',
    install_requires=['django>=1.8'],
    extras_require={
        'factories': ['factory-boy'],
    },
    zip_safe=False,
    keywords='django-email-queue',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Django :: 1.10',
        'Intended Audience :: Developers',
        'Environment :: Web Environment',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    test_suite='runtests.run_tests',
    tests_require=tests_require,
    # https://docs.pytest.org/en/latest/goodpractices.html#integrating-with-setuptools-python-setup-py-test-pytest-runner
    setup_requires=['pytest-runner'],
)
