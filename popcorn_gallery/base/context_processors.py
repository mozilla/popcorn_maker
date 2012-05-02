from django.conf import settings

def common(request):
    return {
        'SITE_URL': settings.SITE_URL
        }
