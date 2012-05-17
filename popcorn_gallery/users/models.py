import base64
import hashlib

from django.contrib.auth.models import User
from django.db import models
from django.db.models import signals

from tower import ugettext_lazy as _


class Profile(models.Model):
    user = models.OneToOneField(User, primary_key=True,
                                verbose_name=_(u'User'))
    name = models.CharField(max_length=255, blank=True,
                            verbose_name=_(u'Display name'))
    website = models.URLField(verbose_name=_(u'Website'), max_length=255,
                              blank=True)
    bio = models.TextField(verbose_name=_(u'Bio'), blank=True)
    featured = models.BooleanField(default=False)
    categories = models.ManyToManyField('popcorn.ProjectCategory',
                                        through='popcorn.ProjectCategoryMembership')

    def __unicode__(self):
        """Return a string representation of the user."""
        return self.display_name

    @models.permalink
    def get_absolute_url(self):
        return ('users_profile', (), {
            'username': self.user.username,
        })

    @property
    def username_hash(self):
        """
        Return a hash of the users email. Used as a URL component when no
        username is set (as is the case with users signed up via BrowserID).
        """
        return base64.urlsafe_b64encode(
            hashlib.sha1(self.user.email).digest()).rstrip('=')

    @property
    def gravatar_url(self):
        return '//www.gravatar.com/avatar/%s ' % hashlib.md5(
            self.user.email.lower()).hexdigest()

    @property
    def has_chosen_identifier(self):
        """Determine if user has a generated or chosen public identifier.."""
        return self.name or (not self.user.username == self.username_hash)

    @property
    def masked_email(self):
        """
        If a user does not have a display name or a username, their email may
        be displayed on their profile. This returns a masked copy so we don't
        leak that data.
        """
        user, domain = self.user.email.split('@')
        mask_part = lambda s, n: s[:n] + u"\u2026" + s[-1:]
        return '@'.join(
            (mask_part(user, len(user) / 3),
             mask_part(domain, 1)))

    @property
    def display_name(self):
        """Choose and return the best public display identifier for a user."""
        if self.name:
            return self.name
        if self.has_chosen_identifier:
            return self.user.username
        return self.masked_email


def create_profile(sender, instance, created, raw, using, *args, **kwargs):
    """Creates an empty ``Profile`` after the User has been created"""
    if created:
        Profile.objects.create(user=instance)
    return

signals.post_save.connect(create_profile, sender=User)
