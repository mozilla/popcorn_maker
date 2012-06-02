from django.db import models

from ..popcorn.storage import TemplateStorage

def asset_path(instance, filename):
    """Determines the path from the author username and the Template shortcode"""
    return '/'.join([instance.template.author.username,
                     instance.template.slug,
                     filename])


class Asset(models.Model):
    template = models.ForeignKey('popcorn.Template')
    asset = models.FileField(upload_to=asset_path, blank=True,
                             storage=TemplateStorage())

    def __unicode__(self):
        return 'Asset: %s' % self.asset
