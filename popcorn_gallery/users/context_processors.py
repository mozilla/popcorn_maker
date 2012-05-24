from urllib import urlencode
from urlparse import urljoin

from django.contrib.auth import REDIRECT_FIELD_NAME
from django.core.urlresolvers import reverse


def browserid_target_processor(request):
    """Build a target URL for the BrowserID login form.
    Where possible, we want to keep the user on the page they're currently on.
    Unfortunate assumption: this assumes the BrowserID view isn't using a
    custom value for the redirect field.
    """
    form_target = reverse('browserid_verify')
    RFN = REDIRECT_FIELD_NAME
    # Respect explicit 'next page' parameters, for example on the login page
    if request.GET.get(RFN):
        if request.GET.get(RFN):
            query_string = urlencode({RFN: request.GET[RFN]})
            form_target = urljoin(form_target, '?' + query_string)
    else:
        # Craft a URL to take them back to the current page
        query_string = urlencode({RFN: request.get_full_path()})
        form_target = urljoin(form_target, '?' + query_string)
    return {'browserid_target': form_target}
