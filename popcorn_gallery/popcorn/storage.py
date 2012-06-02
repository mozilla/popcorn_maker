from django.core.files import storage
from django.conf import settings


class TemplateStorage(storage.FileSystemStorage):

    def __init__(self, *args, **kwargs):
        (super(TemplateStorage, self)
         .__init__(location=settings.TEMPLATE_MEDIA_ROOT,
                   base_url=settings.TEMPLATE_MEDIA_URL, *args, **kwargs))
