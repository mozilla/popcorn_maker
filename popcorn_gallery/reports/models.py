from django.db import models

from django_extensions.db.fields import CreationDateTimeField


class Report(models.Model):
    url = models.URLField()
    description = models.TextField()
    created = CreationDateTimeField()
    is_reviewed = models.BooleanField(default=False)

    def __unicode__(self):
        return u'Report of %s' % self.url

    @models.permalink
    def get_absolute_url(self):
        return ('admin:reports_report_change', [self.id])
