import os

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
