import os

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from ...utils import list_popcorn_assets, list_butter_assets


class Command(BaseCommand):
    """Import the Popcorn plugins"""

    def handle(self, *args, **kwargs):
        popcorn_path = '%s/' % os.path.join(settings.PROJECT_ROOT, 'assets')
        for asset in list_butter_assets(popcorn_path):
            print 'https://popcornmaker-dev.allizom.org%s%s' % (settings.STATIC_URL,
                                                               asset)
        print "Import completed"
