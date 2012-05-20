from .models import Notice


def notifications(request):
    return {'notice_list':  Notice.live.all()[:5]}
