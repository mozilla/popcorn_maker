import os
import manage

from fabric.api import run, local, env, get, prompt, sudo
from fabric.colors import yellow
from fabric.contrib import console, django

from fabric.context_managers import lcd

django.settings_module('popcorn_gallery.settings')
from django.conf import settings


def test(*args):
    """Run the tests locally takes a list of apps to test as arguments"""
    os.environ['FORCE_DB'] =  '1'
    print yellow('Runing tests')
    with lcd(settings.PROJECT_ROOT):
        local('python manage.py test --noinput '
              '--settings=popcorn_gallery.settings.test')


def update_npm():
    print yellow('Updating npm')
    with lcd(os.path.join(settings.PROJECT_ROOT, 'butter')):
        local('npm install')
        local('npm update')

def prepare_butter():
    print yellow('Compiling Butter files.')
    with lcd(os.path.join(settings.PROJECT_ROOT, 'butter')):
        local('node make')
    copy_butter()


def syncdb():
    print yellow('Syncing the database')
    with lcd(settings.PROJECT_ROOT):
        local('python manage.py syncdb --noinput')
        local('python manage.py migrate --noinput')


def copy_butter():
    print yellow('Coping Butter styling')
    with lcd(settings.PROJECT_ROOT):
        local('cp butter/dist/* assets/dist/')
        local('cp butter/dist/*.css assets/css/')
        local('cp butter/dist/*.js assets/js/')


def update_index():
    print yellow('Updating search index')
    with lcd(settings.PROJECT_ROOT):
        local('python manage.py update_index')


def update():
    print yellow('Updating the site:')
    syncdb()
    prepare_butter()
    copy_butter()
    update_index()


def collectstatic():
    prepare_butter()
    print yellow('Collecting static files.')
    with lcd(settings.PROJECT_ROOT):
        local('python manage.py collectstatic --noinput')

