from django.shortcuts import render
from django.http import Http404

from voting.views import vote_on_object
from ..popcorn.models import Project, Template


def homepage(request):
    project_list = Project.live.filter(is_featured=True)[:3]
    context = {'project_list': project_list}
    return render(request, 'homepage.html', context)


def vote(request, model, object_id, direction):
    """Thin wrapper around ``django-voting`` to pass our custom params"""
    if not request.method == 'POST':
        raise Http404
    model_list = {
        'project': Project,
        'template': Template,
        }
    if model not in model_list:
        raise Http404
    model = model_list[model]
    return vote_on_object(request, model=model, allow_xmlhttprequest=True,
                          object_id=object_id, direction=direction)
