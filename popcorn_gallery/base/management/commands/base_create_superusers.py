from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User


class Command(BaseCommand):
    """Make any mozilla registered user an admin"""

    def handle(self, *args, **kwargs):
        for user in User.objects.filter(email__endswith='@mozillafoundation.org',
                                        is_active=True):
            user.is_staff = True
            user.is_superuser = True
            user.save()
            print "Processed %s" % user
