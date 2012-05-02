from django.db import models
from django_extensions.db.fields import (CreationDateTimeField,
                                         ModificationDateTimeField, UUIDField)
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
    author = models.ForeignKey('auth.User')
    template = models.ForeignKey('popcorn.Template')
    metadata = models.TextField()
    html = models.TextField()
    status = models.IntegerField(choices=STATUS_CHOICES, default=LIVE)
    created = CreationDateTimeField()
    modified = ModificationDateTimeField()

    def __unicode__(self):
        return u'Project %s from %s' % (self.name, self.author)

    @property
    def butter_data(self):
        """Returns the Project data for ``Butter``"""
        return {
            '_id': self.uuid,
            'name': self.name,
            'template': self.template.name,
            'data': self.metadata,
            'created': self.created,
            'modified': self.modified,
            }
