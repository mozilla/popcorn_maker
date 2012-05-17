import functools
import json

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib import messages
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

from funfactory.urlresolvers import reverse
from ..baseconv import base62
from ..forms import ProjectEditForm
from ..models import Project, ProjectCategory, Template, TemplateCategory


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
def user_project_config(request, project):
    context = {'object': project}
    return render(request, project.template.config, context)


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
        'project': project,
        }
    return render(request, 'project/edit.html', context)


@valid_user_project
def user_project_delete(request, project):
    if not request.user == project.author:
        raise Http404
    if request.method == 'POST':
        messages.success(request, 'Project removed successfully')
        project.delete()
        return HttpResponseRedirect(reverse('users_dashboard'))
    context = {'project': project}
    return render(request, 'project/delete.html', context)


def project_list(request, slug=None):
    if slug:
        category = get_object_or_404(ProjectCategory, slug=slug)
        kwargs = {'categories': category}
    else:
        category = None
        kwargs = {}
    object_list = (Project.live.filter(**kwargs)
                   .order_by('-is_featured','-created'))
    category_list = ProjectCategory.objects.filter(is_featured=True)
    context = {
        'category': category,
        'project_list': object_list,
        'category_list': category_list,
        }
    return render(request, 'project/object_list.html', context)


def template_list(request, slug=None):
    """Lists all the available templates. Filters by category too"""
    if slug:
        category = get_object_or_404(TemplateCategory, slug=slug)
        kwargs = {'categories': category}
    else:
        category = None
        kwargs = {}
    object_list = (Template.live.filter(**kwargs)
                   .order_by('-is_featured', 'name'))
    category_list = TemplateCategory.objects.filter(is_featured=True)
    context = {
        'template_list': object_list,
        'category': category,
        'category_list': category_list,
        }
    return render(request, 'template/object_list.html', context)


def template_detail(request, slug):
    try:
        template = Template.live.get(slug=slug)
    except Template.DoesNotExist:
        raise Http404
    context = {'template': template,
               'object': None}
    return render(request, template.template, context)


def template_summary(request, slug):
    try:
        template = Template.live.get(slug=slug)
    except Template.DoesNotExist:
        raise Http404
    category_list = TemplateCategory.objects.filter(is_featured=True)
    context = {
        'template': template,
        'object': None,
        'category_list': category_list,
        }
    return render(request, 'template/object_detail.html', context)


def template_config(request, slug):
    try:
        template = Template.live.get(slug=slug)
    except Template.DoesNotExist:
        raise Http404
    context = {'template': template,
               'object': None}
    return render(request, template.config, context)
