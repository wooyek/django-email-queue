# coding=utf-8
# Copyright (C) 2015 Janusz Skonieczny
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
import sys
from pathlib import Path
from invoke import run, task

is_win = sys.platform == 'win32'
ROOT_DIR = Path(__file__).parent.absolute()
SRC_DIR = ROOT_DIR / 'src'
VENV_DIR = ROOT_DIR / ".pve"
VENV_BIN = VENV_DIR / ("Scripts" if is_win else "bin")
PYTHON = VENV_BIN / 'python'
PIP = VENV_BIN / 'pip'
MANAGE = '{} {} '.format(PYTHON, SRC_DIR / 'manage.py')

logging.basicConfig(format='%(asctime)s %(levelname)-7s %(thread)-5d %(filename)s:%(lineno)s | %(funcName)s | %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)
logging.disable(logging.NOTSET)
logging.debug('Loading %s', __name__)


@task
def bump(ctx, patch=True):
    run("git checkout develop")
    run("git pull origin develop --verbose")
    run("git push origin develop --verbose")
    run("git checkout master")
    run("git merge develop --verbose")
    run("git pull origin master --verbose")
    if patch:
        run("bumpversion patch --no-tag")
    else:
        run("bumpversion minor")
    run("git push origin master --verbose")
    run("git checkout develop")
    run("git merge master --verbose")
    run("git push origin develop --verbose")


@task
def register_pypi(ctx):
    run("git checkout master")
    run("python setup.py register -r pypi")


@task
def upload_pypi(ctx):
    run("git checkout master")
    run("python setup.py sdist upload -r pypi")


@task(bump, upload_pypi)
def release(ctx):
    """
    Collect and compile assets, add, commit and push to production remote
    """
