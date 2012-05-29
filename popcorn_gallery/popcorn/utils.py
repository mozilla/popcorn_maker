import os
import datetime
import hashlib

from django.core.cache import cache

from dateutil.relativedelta import relativedelta
from .models import Template


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
            if item.endswith('.html'):
                data['template'] = '%s/%s/%s' % (prefix, candidate, item)
            if item.endswith('.cfg'):
                data['config'] = '%s/%s/%s' % (prefix, candidate, item)
        # all attributes mean a valid template
        if not all(k in data for k in ('slug', 'template', 'config')):
            continue
        try:
            # Already imported
            Template.objects.get(slug=candidate)
            continue
        except Template.DoesNotExist:
            pass
        data['name'] = candidate
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
    cache_expiration = item.modified + relativedelta(minutes=10)
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
        'default': ['-is_featured','-created'],
        }
    if kwargs:
        available_order.update(kwargs)
    order = request_get.get('order')
    if order and order in available_order:
        return available_order[order]
    return available_order['default']
