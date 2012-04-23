from django.db import models
from django.contrib.auth.models import User
from django_extensions.db.fields import (CreationDateTimeField,
                                         ModificationDateTimeField, UUIDField)
from tastypie.models import create_api_key
from tower import ugettext_lazy as _


class Template(models.Model):
    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class Project(models.Model):
    """Popcorn projects"""
    LIVE = 1
    HIDDEN = 2
    REMOVED = 3
    STATUS_CHOICES = (
        (LIVE, _('Live')),
        (HIDDEN, _('Hidden')),
        )
    uuid = UUIDField(unique=True)
    name = models.CharField(max_length=255)
    user = models.ForeignKey('auth.User')
    template = models.ForeignKey('popcorn.Template')
    metadata = models.TextField()
    html = models.TextField()
    status = models.IntegerField(choices=STATUS_CHOICES, default=LIVE)
    created = CreationDateTimeField()
    modified = ModificationDateTimeField()

    def __unicode__(self):
        return u'Project %s from %s' % (self.name, self.user)


models.signals.post_save.connect(create_api_key, sender=User,
                                 dispatch_uid='tastypie.create_api_key')
