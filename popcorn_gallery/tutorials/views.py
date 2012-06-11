from django.http import Http404
from django.shortcuts import get_object_or_404, render

from .models import Tutorial


def object_detail(request, slug):
    tutorial = get_object_or_404(Tutorial, slug=slug)
    if tutorial.is_published or request.user.is_superuser:
        return render(request, 'tutorial/object_detail.html',
                      {'tutorial': tutorial})
    raise Http404


def object_list(request):
    tutorial_list = Tutorial.objects.filter(status=Tutorial.LIVE)
    return render(request, 'tutorial/object_list.html',
                  {'tutorial_list': tutorial_list})
