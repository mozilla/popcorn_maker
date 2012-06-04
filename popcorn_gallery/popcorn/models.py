from django.conf import settings
from django.db import models
from django.utils.encoding import smart_unicode

from django_extensions.db.fields import (CreationDateTimeField,
                                         ModificationDateTimeField, UUIDField,
                                         AutoSlugField)
from django_extensions.db.fields.json import JSONField
from taggit.managers import TaggableManager
from tower import ugettext_lazy as _

from .baseconv import base62
from .managers import ProjectManager, ProjectLiveManager, TemplateManager
from .storage import TemplateStorage
from .templates import prepare_template_stream, remove_default_values
from ..attachments.models import Asset
from ..base.decorators import cached_property


def template_path(instance, filename):
    """Saves the template in a location determined by the ``author`` and
    the ``slug`` of the project"""
    return '/'.join([instance.author.username, instance.slug, filename])


class Template(models.Model):
    """Template is a group of assets which allows the user interact with Butter
    They have an html start point which is ``template``
    """
    LIVE = 1
    HIDDEN = 2
    REMOVED = 3
    STATUS_CHOICES = (
        (LIVE, _('Published')),
        (HIDDEN, _('Unpublished')),
        (REMOVED, _('Removed')),
        )
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    author = models.ForeignKey('auth.User')
    config = JSONField(blank=True,
                       help_text=_(u'Any extra data that the template requires '
                                   'default values such as the baseDir and '
                                   'template name are automatically added'))
    metadata = models.TextField(blank=True)
    template_content = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to=template_path, blank=True,
                                  storage=TemplateStorage())
    is_featured = models.BooleanField(default=False)
    status = models.IntegerField(choices=STATUS_CHOICES, default=LIVE)
    categories = models.ManyToManyField('popcorn.TemplateCategory', blank=True)
    tags = TaggableManager(blank=True)
    created = CreationDateTimeField()
    modified = ModificationDateTimeField()
    views_count = models.IntegerField(default=0)
    votes_count = models.IntegerField(default=0)

    # managers
    objects = models.Manager()
    live = TemplateManager()

    class Meta:
        ordering = ('-is_featured', 'name')

    def __unicode__(self):
        return self.name

    def save(self, *args, **kwargs):
        base_url = '%s%s' % (settings.TEMPLATE_MEDIA_URL,
                                 template_path(self, ''))
        if self.template_asset and not self.template_content:
            template_stream = smart_unicode(self.template_asset.read())
            self.template_content = prepare_template_stream(template_stream,
                                                            base_url)
        if self.config_asset and not self.config:
            config_stream = smart_unicode(self.config_asset.read())
            self.config = remove_default_values(config_stream, base_url)
        if self.metadata_asset and not self.metadata:
            metadata_stream = smart_unicode(self.metadata_asset.read())
            self.metadata = remove_default_values(metadata_stream, base_url)
        return super(Template, self).save(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return ('template_summary', [self.slug])

    @models.permalink
    def get_template_url(self):
        return ('template_detail', [self.slug])

    @cached_property
    def asset_list(self):
        return self.asset_set.all()

    @cached_property
    def template_asset(self):
        for asset in self.asset_list:
            if asset.asset_type == Asset.TEMPLATE:
                return asset.asset
        return None

    @cached_property
    def config_asset(self):
        for asset in self.asset_list:
            if asset.asset_type == Asset.CONFIG:
                return asset.asset
        return None

    @cached_property
    def metadata_asset(self):
        for asset in self.asset_list:
            if asset.asset_type == Asset.DATA:
                return asset.asset
        return None


class TemplateCategory(models.Model):
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from='name')
    is_featured = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = u'Template Categories'

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('template_list_category', [self.slug])


class Project(models.Model):
    """Popcorn projects"""
    LIVE = 1
    HIDDEN = 2
    REMOVED = 3
    STATUS_CHOICES = (
        (LIVE, _('Published')),
        (HIDDEN, _('Unpublished')),
        (REMOVED, _('Removed')),
        )
    uuid = UUIDField(unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    author = models.ForeignKey('auth.User')
    url = models.URLField(blank=True)
    thumbnail = models.ImageField(upload_to="projects", blank=True)
    template = models.ForeignKey('popcorn.Template', blank=True, null=True)
    metadata = models.TextField()
    html = models.TextField(blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=HIDDEN)
    is_shared = models.BooleanField(default=False)
    is_forkable = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    created = CreationDateTimeField()
    modified = ModificationDateTimeField()
    categories = models.ManyToManyField('popcorn.ProjectCategory', blank=True)
    source = models.ForeignKey('popcorn.Project', blank=True, null=True,
                               on_delete=models.SET_NULL)
    views_count = models.IntegerField(default=0)
    votes_count = models.IntegerField(default=0)

    # managers
    objects = ProjectManager()
    live = ProjectLiveManager()

    class Meta:
        ordering = ('is_featured', '-modified', )

    def __unicode__(self):
        return u'Project %s from %s' % (self.name, self.author)

    @models.permalink
    def get_permalink_for(self, name):
        return (name, [self.author.username, self.shortcode])

    def get_absolute_url(self):
        return self.get_permalink_for('user_project_summary')

    def get_project_url(self):
        return self.get_permalink_for('user_project')

    def get_edit_url(self):
        return self.get_permalink_for('user_project_edit')

    def get_delete_url(self):
        return self.get_permalink_for('user_project_delete')

    @models.permalink
    def get_api_url(self):
        return ('api:project_detail', [self.uuid])

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

    @property
    def is_published(self):
        return self.status == self.LIVE

    @property
    def shortcode(self):
        return base62.from_decimal(self.pk)

    @property
    def is_external(self):
        return all([self.url])

    @property
    def is_removed(self):
        return self.status == self.REMOVED

    def available_for(self, user):
        """Determines if the ``Project`` is available for the given ``User``"""
        if self.status == self.REMOVED:
            return False
        if user == self.author or self.status == self.LIVE:
            return True
        return False


class ProjectCategory(models.Model):
    name = models.CharField(max_length=255)
    slug = AutoSlugField(populate_from='name')
    is_featured = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = u'Project Categories'

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('project_list_category', [self.slug])


class ProjectCategoryMembership(models.Model):
    """Intermediary Model to determine when a user is member of a given
    ``ProjectCategory``"""
    APPROVED = 1
    PENDING = 2
    DENIED = 3
    STATUS_CHOICES = (
        (APPROVED, _('Approved')),
        (PENDING, _('Pending')),
        (DENIED, _('Denied')),
        )
    user = models.ForeignKey('users.Profile')
    project_category = models.ForeignKey('popcorn.ProjectCategory')
    status = models.IntegerField(choices=STATUS_CHOICES, default=PENDING)
    created = CreationDateTimeField()
    modified = ModificationDateTimeField()

    class Meta:
        unique_together = ('user', 'project_category')

    def __unicode__(self):
        return u'%s membership for %s: %s' %(self.project_category,
                                                self.user,
                                                self.get_status_display())
