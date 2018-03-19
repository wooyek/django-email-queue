# coding=utf-8
# Copyright (C) 2018 Janusz Skonieczny
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import logging
import os
import shutil
import sys
from itertools import chain
from pathlib import Path

from invoke import call, task

logging.basicConfig(format='%(asctime)s %(levelname)-7s %(thread)-5d %(filename)s:%(lineno)s | %(funcName)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
# logging.getLogger().setLevel(logging.INFO)
# logging.disable(logging.NOTSET)
logging.debug('Loading %s', __name__)

log = logging.getLogger(__name__)

is_win = sys.platform == 'win32'
ROOT_DIR = Path(__file__).parent.absolute()
SRC_DIR = ROOT_DIR / 'src'
VENV_DIR = ROOT_DIR / ".pve"
VENV_BIN = VENV_DIR / ("Scripts" if is_win else "bin")
PYTHON = VENV_BIN / 'python'
PIP = VENV_BIN / 'pip'
MANAGE = '{} {} '.format(PYTHON, SRC_DIR / 'manage.py')


@task
def clean(ctx):
    for item in chain(Path(ROOT_DIR).rglob("*.pyc"), Path(ROOT_DIR).rglob("*.pyo")):
        logging.debug("Deleting: %s", item)
        item.unlink()

    for item in Path(ROOT_DIR).rglob("__pycache__"):
        logging.debug("Deleting: %s", item)
        shutil.rmtree(str(item), ignore_errors=True)

    shutil.rmtree(str(ROOT_DIR / 'build'), ignore_errors=True)
    shutil.rmtree(str(ROOT_DIR / 'example_project' / '.eggs'), ignore_errors=True)
    shutil.rmtree(str(ROOT_DIR / '.eggs'), ignore_errors=True)
    shutil.rmtree(str(ROOT_DIR / '.tox'), ignore_errors=True)
    shutil.rmtree(str(ROOT_DIR / '.tmp'), ignore_errors=True)
    shutil.rmtree(str(ROOT_DIR / '.coverage'), ignore_errors=True)
    shutil.rmtree(str(ROOT_DIR / '.htmlcov'), ignore_errors=True)
    shutil.rmtree(str(ROOT_DIR / '.pytest_cache'), ignore_errors=True)
    shutil.rmtree(str(ROOT_DIR / '.cache'), ignore_errors=True)
    ctx.run('git checkout -- .tmp')


@task
def lint(ctx):
    """Check project codebase cleanness"""
    ctx.run("flake8 src tests setup.py manage.py")
    ctx.run("isort --check-only --diff --recursive src tests setup.py")
    ctx.run("python setup.py check --strict --metadata --restructuredtext")
    ctx.run("check-manifest  --ignore .idea,.idea/* .")


@task
def detox(ctx):
    envs = ctx.run("tox -l").stdout.splitlines()
    ctx.run("detox " + ",".join(env for env in envs[:-1]))
    ctx.run("tox " + envs[-1])


@task
def register_pypi(ctx):
    """Register project on PyPi"""
    ctx.run("git checkout master")
    ctx.run("python setup.py register -r pypi")


@task
def register_pypi_test(ctx):
    """Register project on TEST PyPi"""
    ctx.run("git checkout master")
    ctx.run("python setup.py register -r pypitest")


@task
def upload_pypi(ctx):
    """Upload to PyPi"""
    ctx.run("python setup.py sdist upload -r pypi")
    ctx.run("python setup.py bdist_wheel upload -r pypi")


@task(clean)
def dist(ctx):
    ctx.run("python setup.py sdist")
    ctx.run("python setup.py bdist_wheel")
    ctx.run("ls -l dist")


@task(clean)
def install(ctx):
    ctx.run("python setup.py install")


@task
def sync(ctx):
    """Sync master and develop branches in both directions"""
    ctx.run("git checkout develop")
    ctx.run("git pull origin develop --verbose")

    ctx.run("git checkout master")
    ctx.run("git pull origin master --verbose")

    ctx.run("git checkout develop")
    ctx.run("git merge master --verbose")

    ctx.run("git checkout master")
    ctx.run("git merge develop --verbose")

    ctx.run("git checkout develop")


@task
def bump(ctx, minor=True):
    """Increment version number"""
    if minor:
        ctx.run("bumpversion minor")
    else:
        ctx.run("bumpversion patch --no-tag")


@task()
def upgrade(ctx):
    """Upgrade frozen requirements to the latest version"""
    ctx.run('pip-compile requirements.in -o requirements.txt --verbose --upgrade')
    ctx.run('sort requirements.txt -o requirements.txt')
    with (ROOT_DIR / 'requirements.txt').open('a') as f:
        f.write('--find-links=requirements')
    ctx.run('git add requirements.txt')
    ctx.run('git commit -m "Requirements upgrade"')


@task(lint, sync, bump)
def release(ctx):
    """Build new package version release and sync repo"""
    ctx.run("git checkout develop")
    ctx.run("git merge master --verbose")

    ctx.run("git push origin develop --verbose")
    ctx.run("git push origin master --verbose")


@task(release, upload_pypi)
def publish(ctx):
    """Release and upload new version"""


@task
def locales(ctx):
    """
    Collect and compile translation strings
    """
    # https://docs.djangoproject.com/en/dev/ref/django-admin/#django-admin-makemessages
    """
    python manage.py makemessages -v 3 --no-wrap --ignore ".*" --locale=pl_PL
    python manage.py compilemessages -v 3
    """
    tmp = ROOT_DIR / ".tmp"
    if not tmp.exists():
        os.makedirs(str(tmp))
    locale = ROOT_DIR / "src" / "locale"
    if not locale.exists():
        os.makedirs(str(locale))
    # http://babel.edgewall.org/wiki/BabelDjango
    pybabel = str(VENV_BIN / 'pybabel')
    ctx.run(pybabel + " extract -F locale/babel.cfg -o locale/django.pot --no-wrap --sort-output .")
    # create locales firs
    # pybabel init -D django -i locale/django.pot -d locale -l es
    # http://babel.edgewall.org/wiki/BabelDjango#CreatingandUpdatingTranslationsCatalogs
    # ctx.run(pybabel + " update -D django -i locale/django.pot -d locale --ignore-obsolete")
    ctx.run(pybabel + " update -D django -i locale/django.pot -d locale --previous --no-wrap")
    ctx.run(pybabel + " compile -D django -d locale --statistics")
    log.info("JavaScript locales")
    # ctx.run(pybabel + " update -D djangojs -i locale/djangojs.pot -d locale --previous --no-wrap")
    ctx.run("django-admin makemessages -d djangojs -i static -i node_modules")
    ctx.run(pybabel + " compile -D djangojs -d locale --statistics")

