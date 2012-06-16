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
from .storage import TemplateStorage


def get_valid_file_regex(file_extensions):
    valid_extensions = "|".join(file_extensions)
    regex = '([-\.\w]+\.(?:%s))' % valid_extensions
    return re.compile(regex)


def get_valid_file_list(path_base, path_list, file_extensions):
    """Returns a list of valid files from the given path,
    with the right extension"""
    pattern = get_valid_file_regex(file_extensions)
    valid_file_list = []
    for current_path in path_list:
        for root, dirs, files in os.walk(current_path):
            # any of the directories is hidden
            if any([p.startswith('.') for p in root.split('/')]):
                continue
            base_url = root.replace(path_base, '')
            url = lambda x: '%s/%s' % (base_url, x)
            # add the files that match our extensions
            valid_file_list += [url(f) for f in files if pattern.match(f)]
    return valid_file_list


def list_popcorn_assets(butter_path):
    """Lists the the current popcorn assets"""
    popcorn_path = os.path.join(butter_path, 'external', 'popcorn-js')
    return get_valid_file_list(butter_path, [popcorn_path], ['js'])


def list_butter_assets(butter_path):
    butter_paths = [
        os.path.join(butter_path, 'dist'),
        ]
    return get_valid_file_list(butter_path, butter_paths, ['js', 'css'])


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
    pattern = get_valid_file_regex(['html', 'jpg', 'png', 'css', 'js', 'json',
                                    'gif'])
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
