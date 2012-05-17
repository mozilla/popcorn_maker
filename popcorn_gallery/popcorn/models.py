import os

from django.conf import settings
from django.db import models
from django_extensions.db.fields import (CreationDateTimeField,
                                         ModificationDateTimeField, UUIDField,
                                         AutoSlugField)
from tower import ugettext_lazy as _

from .managers import ProjectManager, TemplateManager
from .baseconv import base62


def get_templates(prefix='butter', extension=None):
    """List the files with the given extension"""
    template_choices = []
    if extension:
        extension = '.%s' % extension
    new_path = os.path.join(settings.POPCORN_TEMPLATES_ROOT, prefix)
    for root, dir_list, file_list in os.walk(new_path):
        for template in file_list:
            full_path = os.path.join(root, template)
            template_path = full_path.replace(new_path, '')
            template_full_path = '%s%s' % (prefix, template_path)
            if extension and template_path.endswith(extension):
                template_choices.append((template_full_path, template_path))
    return template_choices


class Template(models.Model):
    LIVE = 1
    HIDDEN = 2
    STATUS_CHOICES = (
        (LIVE, _('Published')),
        (HIDDEN, _('Unpublished')),
        )
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    template = models.CharField(max_length=255,
                                choices=get_templates(extension='html'))
    config = models.CharField(max_length=255,
                              choices=get_templates(extension='cfg'))
    thumbnail = models.ImageField(upload_to="templates", blank=True)
    is_featured = models.BooleanField(default=False)
    status = models.IntegerField(choices=STATUS_CHOICES, default=LIVE)
    categories = models.ManyToManyField('popcorn.TemplateCategory', blank=True)

    # managers
    objects = models.Manager()
    live = TemplateManager()

    class Meta:
        ordering = ('-is_featured', 'name')

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('template_detail', [self.slug])


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
    STATUS_CHOICES = (
        (LIVE, _('Published')),
        (HIDDEN, _('Unpublished')),
        )
    uuid = UUIDField(unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    author = models.ForeignKey('auth.User')
    template = models.ForeignKey('popcorn.Template')
    metadata = models.TextField()
    html = models.TextField()
    status = models.IntegerField(choices=STATUS_CHOICES, default=LIVE)
    is_shared = models.BooleanField(default=True)
    is_forkable = models.BooleanField(default=True)
    is_removed = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    created = CreationDateTimeField()
    modified = ModificationDateTimeField()
    categories = models.ManyToManyField('popcorn.ProjectCategory', blank=True)

    # managers
    objects = models.Manager()
    live = ProjectManager()

    class Meta:
        ordering = ('is_featured', '-modified', )

    def __unicode__(self):
        return u'Project %s from %s' % (self.name, self.author)

    @models.permalink
    def get_absolute_url(self):
        return ('user_project', [self.author.username, self.shortcode])

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
