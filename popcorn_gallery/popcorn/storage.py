from django.core.files import storage
from django.conf import settings


class TemplateStorage(storage.FileSystemStorage):

    def __init__(self, *args, **kwargs):
        (super(TemplateStorage, self)
         .__init__(location=settings.TEMPLATE_MEDIA_ROOT,
                   base_url=settings.TEMPLATE_MEDIA_URL, *args, **kwargs))

    def get_available_name(self, name):
        """Returns a filename that's free on the target storage system, and
        available for new content to be written to.
        If the file exists overwrite it.
        """
        # If the filename already exists, remove it as if
        # it was a true file system
        if self.exists(name):
            self.delete(name)
        return name
