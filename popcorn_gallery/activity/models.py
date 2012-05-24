from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from django_extensions.db.fields import CreationDateTimeField
from tower import ugettext as _
from .managers import ActivityManager
from ..popcorn.models import Project


class Activity(models.Model):
    """Records recent activity on the profile"""
    user = models.ForeignKey('auth.User')
    body = models.CharField(max_length=255)
    created = CreationDateTimeField()
    url = models.URLField(blank=True)

    # managers
    objects = ActivityManager()

    class Meta:
        verbose_name_plural = 'activities'

    def __unicode__(self):
        return u'Activity: %s %s' % (self.user, self.body)

    def get_absolute_url(self):
        return self.url if self.url else None


@receiver(post_save, sender=Project, dispatch_uid='activity_project_create')
def created_project(sender, *args, **kwargs):
    instance = kwargs.pop('instance')
    message = None
    if kwargs['created'] and instance.is_published:
        message = _('has created a project')
    if kwargs['created'] and instance.source:
        message = _('has forked a project')
    if message:
        Activity.objects.create(user=instance.author, body=message,
                                url=instance.get_absolute_url())
    return


@receiver(pre_save, sender=Project, dispatch_uid='activity_project_update')
def updated_project(sender, *args, **kwargs):
    instance = kwargs.pop('instance')
    if instance.id and instance.is_published:
        project = (Project.objects.get(id=instance.id))
        # status has changed
        if not project.status == instance.status:
            Activity.objects.create(user=instance.author,
                                    body=_('has published a project'),
                                    url=instance.get_absolute_url())
    return
