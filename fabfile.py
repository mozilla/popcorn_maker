import os
import manage

from fabric.api import run, local, env, get, prompt, sudo
from fabric.colors import yellow


def test(*args):
    """Run the tests locally takes a list of apps to test as arguments"""
    os.environ['FORCE_DB'] =  '1'
    print yellow('Testing')
    local('python manage.py test --noinput '
          '--settings=popcorn_gallery.settings.test')

def collectstatic():
    print yellow('Collecting static files')
    local('python manage.py collectstatic --noinput')
