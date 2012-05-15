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

def compile_butter():
    print yellow('Compiling Butter files.')
    with lcd(os.path.join(settings.PROJECT_ROOT, 'butter')):
        local('node make')

def collectstatic():
    compile_butter()
    print yellow('Collecting static files.')
    with lcd(settings.PROJECT_ROOT):
        local('python manage.py collectstatic --noinput')

