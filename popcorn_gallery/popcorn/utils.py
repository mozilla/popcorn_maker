import os
import re
import datetime
import hashlib

from zipfile import ZipFile
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.conf import settings

from dateutil.relativedelta import relativedelta
from voting.models import Vote
from .models import Template
from .storage import TemplateStorage


def import_popcorn_templates(popcorn_path, prefix):
    """Import the templates from the path provided with the following conventions:
    - The folder name will be the slug and named used for the template
    - The folders must contain a ``.cfg`` file and an ``.html`` file.
    """
    candidates = [n for n in os.listdir(popcorn_path) if os.path.isdir(os.path.join(popcorn_path, n)) ]
    for candidate in candidates:
        data = {'slug': candidate}
        candidate_path = os.path.join(popcorn_path, candidate)
        for item in os.listdir(candidate_path):
            # TODO: get template data and import assets
            assert False, (prefix, candidate, item)
        try:
            # Already imported
            Template.objects.get(slug=candidate)
            continue
        except Template.DoesNotExist:
            pass
        Template.objects.create(**data)
    return


def update_views_count(item):
    """Updates the visitor count on a given ``object`` updates the count
    in the object after 10 minutes
    The object must have
     - ``views_count`` field
    """
    key = 'views%s' % (hashlib.md5('%s%s' % (item.id, type(item)))
                       .hexdigest())
    if cache.get(key):
        views_count = cache.get(key) + 1
    else:
        views_count = item.views_count + 1
    cache.set(key, views_count)
    cache_expiration = item.modified + relativedelta(minutes=settings.CACHE_OBJECT_METADATA)
    if datetime.datetime.utcnow() > cache_expiration:
        item.views_count = views_count
        item.save()
    return views_count


def get_order_fields(request_get, **kwargs):
    """Determines the ordering of the fields by inspecting the
    ``order`` passed in the request GET"""
    available_order = {
        'views': ['-views_count', '-created'],
        'created': ['-created'],
        'votes': ['-votes_count', '-created'],
        'default': ['-is_featured', '-created'],
        }
    if kwargs:
        available_order.update(kwargs)
    order = request_get.get('order')
    if order and order in available_order:
        return available_order[order]
    return available_order['default']


def update_vote_score(item):
    """Caches the ``vote_score`` for ordering"""
    votes = Vote.objects.get_score(item)
    cache_expiration = item.modified + relativedelta(minutes=settings.CACHE_OBJECT_METADATA)
    if datetime.datetime.utcnow() > cache_expiration \
        and votes['score'] > item.votes_count:
        item.votes_count = votes['score']
        item.save()
    return votes


def import_zipped_template(zipped_template, base_path, storage_class=TemplateStorage):
    """Uncompress a zipped file and imports it using the given ``Storage``"""
    valid_extensions = "|".join(['html', 'jpg', 'png', 'css', 'js', 'json',
                                 'gif'])
    regex = '([-\w]+\.(?:%s))' % valid_extensions
    pattern = re.compile(regex)
    template_files = ZipFile(zipped_template)
    saved_files = []
    for file_path in template_files.namelist():
        file_bits = file_path.split('/')
        file_name = file_bits[-1]
        if pattern.match(file_name):
            short_filename = '/'.join(file_bits[1:])
            storage_filename = '%s%s' % (base_path, short_filename)
            storage = storage_class()
            content_file = ContentFile(template_files.read(file_path))
            saved_files.append(storage.save(storage_filename, content_file))
    return saved_files
