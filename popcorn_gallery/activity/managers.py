from django.db import models


class ActivityManager(models.Manager):

    def get_for_user(self, user):
        return self.filter(user=user)
