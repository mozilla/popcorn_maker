from django.db import models

from django_extensions.db.fields import (CreationDateTimeField, AutoSlugField,
                                         ModificationDateTimeField)
from tower import ugettext_lazy as _


class Tutorial(models.Model):
    LIVE = 1
    HIDDEN = 2
    STATUS_CHOICES = (
        (LIVE, _('Published')),
        (HIDDEN, _('Unpublished')),
        )
    title = models.CharField(max_length=255)
    slug = AutoSlugField(unique=True, populate_from='title')
    body = models.TextField()
    url = models.URLField(blank=True)
    thumbnail = models.ImageField(upload_to="tutorials", blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=HIDDEN)
    created = CreationDateTimeField()
    modified = ModificationDateTimeField()

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('tutorial:object_detail', [self.slug])

    @property
    def is_published(self):
        return self.status == self.LIVE
