import os

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from ...utils import import_popcorn_templates


class Command(BaseCommand):
    """Import the Popcorn templates
    - Templates should be contained in a ``butter`` directory.
    """

    def handle(self, *args, **kwargs):
        prefix = 'butter'
        popcorn_path = os.path.join(settings.PROJECT_ROOT, 'templates',
                                    prefix)
        import_popcorn_templates(popcorn_path, prefix)
        print "Import completed"
