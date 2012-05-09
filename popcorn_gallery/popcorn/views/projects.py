import functools
import json

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

from ..baseconv import base62
from ..forms import ProjectEditForm
from ..models import Project, Category


def valid_user_project(func):
    """Decorator that makes sure the project is active and valid"""
    @functools.wraps(func)
    def wrapper(request, *args, **kwargs):
        username = kwargs.pop('username')
        shortcode = kwargs.pop('shortcode')
        try:
            pk = base62.to_decimal(shortcode)
        except Exception:
            raise Http404
        params = {
            'author__username': username,
            'pk': pk,
            'is_removed': False,
            }
        if not request.user.is_authenticated() or \
            not request.user.username == username:
            params['status'] = Project.LIVE
        try:
            project = (Project.objects.select_related('author', 'template')
                       .get(**params))
        except Project.DoesNotExist:
            raise Http404
        return func(request, project, *args, **kwargs)
    return wrapper


@valid_user_project
def user_project(request, project):
    context = {'object': project}
    return render(request, project.template.template, context)


@valid_user_project
def user_project_meta(request, project):
    profile = project.author.get_profile()
    context = {
        'author': profile.name,
        'project': project.name,
        'url': '%s%s' % (settings.SITE_URL, project.get_absolute_url()),
        'created': project.created,
        'modified': project.modified,
        }
    return HttpResponse(json.dumps(context, cls=DjangoJSONEncoder),
                        mimetype='application/json')


@valid_user_project
def user_project_data(request, project):
    context = {
        'error': 'okay',
        # Butter needs the project metadata as a string that can be
        # parsed to JSON
        'project': project.metadata,
        }
    return HttpResponse(json.dumps(context, cls=DjangoJSONEncoder),
                        mimetype='application/json')


@valid_user_project
def user_project_edit(request, project):
    if not request.user == project.author:
        raise Http404
    if request.method == 'POST':
        form = ProjectEditForm(request.POST, instance=project)
        if form.is_valid():
            instance = form.save()
            return HttpResponseRedirect(instance.get_absolute_url())
    else:
        form = ProjectEditForm(instance=project)
    context = {
        'form': form,
        'object': project,
        }
    return render(request, 'project/edit.html', context)


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    project_list = Project.live.filter(categories=category).order_by('-created')
    context = {
        'object': category,
        'project_list': project_list
        }
    return render(request, 'category/object_detail.html', context)
