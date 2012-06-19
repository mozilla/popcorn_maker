from django.db import models

from ..popcorn.storage import TemplateStorage

from tower import ugettext as _


def asset_path(instance, filename):
    """Determines the path from the author username and the Template shortcode"""
    return '/'.join([instance.template.author.username,
                     instance.template.slug,
                     filename])


class Asset(models.Model):
    TEMPLATE = 1
    CONFIG = 2
    DATA = 3
    ASSET_CHOICES = (
        (TEMPLATE, _(u'Template Source')),
        (CONFIG, _(u'Template Configuration')),
        (DATA, _(u'Default Metadata')),
        )
    template = models.ForeignKey('popcorn.Template')
    asset_type = models.IntegerField(blank=True, null=True,
                                     choices=ASSET_CHOICES)
    asset = models.FileField(upload_to=asset_path, blank=True,
                             storage=TemplateStorage())

    def __unicode__(self):
        return 'Asset: %s' % self.asset

    def delete(self, *args, **kwargs):
        # remove the asset from the FileSystem
        self.asset.delete()
        return super(Asset, self).delete(*args, **kwargs)
