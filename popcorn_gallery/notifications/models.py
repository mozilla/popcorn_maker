from django.db import models
from django_extensions.db.fields import CreationDateTimeField

from tower import ugettext_lazy as _
from .managers import NoticeLiveManager


class Notice(models.Model):
    LIVE = 1
    REMOVED = 2
    STATUS_CHOICES = (
        (LIVE, _('Published')),
        (REMOVED, _('Unpublished')),
        )
    title = models.CharField(max_length=255)
    body = models.TextField()
    created = CreationDateTimeField()
    status = models.IntegerField(choices=STATUS_CHOICES, default=LIVE)
    end_date = models.DateTimeField(blank=True, null=True,
                                    help_text='Optional. Determines when the'
                                    'notice dissapears')

    # managers
    objects = models.Manager()
    live = NoticeLiveManager()

    class Meta:
        ordering = ('-created',)

    def __unicode__(self):
        return u'Notice: %s' % self.title
