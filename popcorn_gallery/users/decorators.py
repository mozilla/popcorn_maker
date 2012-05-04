from django.conf import settings
from django.http import HttpResponseRedirect


def anonymous_only(func):
    """
    Opposite of ``django.contrib.auth.decorators.login_required``. This
    decorator is for views that redirect users to the redirect field name
    if they are already logged in.
    """

    def decorator(*args, **kwargs):
        request = args[0]
        if request.user.is_authenticated():
            return HttpResponseRedirect(settings.LOGIN_REDIRECT_URL)
        return func(*args, **kwargs)
    return decorator
