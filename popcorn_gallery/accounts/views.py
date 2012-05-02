from django.http import HttpResponse
from django.utils import simplejson as json

from django_browserid.views import Verify


class AjaxVerify(Verify):
    """Handles AJAX requests for browserid"""

    def login_success(self):
        """Handle a successful login. Use this to perform complex redirects
        post-login. Returns ajax in case of an ajax validation call"""
        result = super(AjaxVerify, self).login_success()
        if self.request.is_ajax():
            response = {
                'status':'okay',
                'email': self.user.email,
                }
            return HttpResponse(json.dumps(response),
                                mimetype='application/json')
        return result

    def login_failure(self):
        """Handle a failed login. Use this to perform complex redirects
        post-login."""
        result = super(AjaxVerify, self).login_failure()
        if self.request.is_ajax():
            return HttpResponse(json.dumps({'status': 'failed'}),
                                mimetype='application/json')
        return result
