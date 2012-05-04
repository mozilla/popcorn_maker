from django.forms.widgets import FileInput
from django.utils.html import escape
from django.utils.safestring import mark_safe


class ImageFileInput(FileInput):
    template_with_initial = u'%(initial)s <br />%(input)s'

    def render(self, name, value, attrs=None):
        template = u'%(input)s'
        substitutions = {
            'input': super(ImageFileInput, self).render(
                name, value, attrs)
        }
        if value and hasattr(value, 'url'):
            template = self.template_with_initial
            substitutions['initial'] = (u'<img src="%s">' % (
                escape(value.url),))
        return mark_safe(template % substitutions)
