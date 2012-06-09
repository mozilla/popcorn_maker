import os

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from ...utils import list_popcorn_assets, list_butter_assets


class Command(BaseCommand):
    """Import the Popcorn plugins"""

    def handle(self, *args, **kwargs):
        popcorn_path = '%s/' % os.path.join(settings.PROJECT_ROOT, 'butter')
        #print list_popcorn_assets(popcorn_path)
        print list_butter_assets(popcorn_path)
        print "Import completed"
