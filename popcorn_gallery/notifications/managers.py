import datetime

from django.db import models
from django.db.models import Q


class NoticeLiveManager(models.Manager):

    def get_query_set(self):
        now = datetime.datetime.utcnow()
        return (super(NoticeLiveManager, self).get_query_set()
                .filter((Q(end_date__gte=now) | Q(end_date__isnull=True)),
                        status=self.model.LIVE))
