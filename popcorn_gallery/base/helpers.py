import jinja2

from jingo import register


from easy_thumbnails.files import get_thumbnailer


@register.function
def thumbnail(image, size, crop=True, **kwargs):
    defaults = {
        'size': size,
        'crop': crop,
        }
    if kwargs:
        defaults.update(kwargs)
    return get_thumbnailer(image).get_thumbnail(defaults).url
