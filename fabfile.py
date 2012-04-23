import os

from fabric.api import local
from fabric.colors import yellow


def test(*args):
    """Run the tests locally takes a list of apps to test as arguments"""
    os.environ['FORCE_DB'] =  '1'
    print yellow('Testing')
    local('python manage.py test --settings=popcorn_gallery.settings.test')
