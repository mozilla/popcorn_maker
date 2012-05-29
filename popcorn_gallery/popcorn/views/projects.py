import functools
import json

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string

from funfactory.urlresolvers import reverse
from tower import ugettext as _
from voting.models import Vote

from ..baseconv import base62
from ..forms import (ProjectEditForm, ExternalProjectEditForm,
                     ProjectSubmissionForm)
from ..models import (Project, ProjectCategory, Template, TemplateCategory,
                      ProjectCategoryMembership)
from ..utils import update_views_count
from ...base.utils import notify_admins


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
        return func(request, project=project, *args, **kwargs)
    return wrapper


def is_popcorn_project(func):
    """Decorator that makes sure that project was made with a
    popcorn ``Template`` """
    @functools.wraps(func)
    def wrapper(request, *args, **kwargs):
        project = kwargs.pop('project')
        if not project.template:
            raise Http404
        return func(request, project, *args, **kwargs)
    return wrapper


@valid_user_project
@is_popcorn_project
def user_project(request, project):
    context = {'project': project, 'template': project.template}
    return render(request, project.template.template, context)


@valid_user_project
@is_popcorn_project
def user_project_config(request, project):
    context = {'project': project }
    return render(request, project.template.config, context)


@valid_user_project
@is_popcorn_project
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
@is_popcorn_project
def user_project_data(request, project):
    context = {
        'error': 'okay',
        # Butter needs the project metadata as a string that can be
        # parsed to JSON
        'project': project.metadata,
        }
    return HttpResponse(json.dumps(context, cls=DjangoJSONEncoder),
                        mimetype='application/json')


@login_required
@valid_user_project
def user_project_edit(request, project):
    if not request.user == project.author:
        raise Http404
    FormClass = ExternalProjectEditForm if project.is_external else ProjectEditForm
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES, instance=project,
                         user=request.user.get_profile())
        if form.is_valid():
            instance = form.save()
            return HttpResponseRedirect(instance.get_absolute_url())
    else:
        form = FormClass(instance=project, user=request.user.get_profile())
    context = {
        'form': form,
        'project': project,
        }
    return render(request, 'project/edit.html', context)


@login_required
@valid_user_project
def user_project_delete(request, project):
    if not request.user == project.author:
        raise Http404
    if request.method == 'POST':
        messages.success(request, _('Project removed successfully'))
        project.delete()
        return HttpResponseRedirect(reverse('users_dashboard'))
    context = {'project': project}
    return render(request, 'project/delete.html', context)


@login_required
@valid_user_project
@is_popcorn_project
def user_project_fork(request, project):
    if not project.is_forkable:
        raise Http404
    if request.method == 'POST':
        messages.success(request, _('Project forked successfully'))
        project = Project.objects.fork(project, request.user)
        return HttpResponseRedirect(project.get_absolute_url())
    context = {'project': project}
    return render(request, 'project/fork.html', context)


@valid_user_project
def user_project_summary(request, project):
    update_views_count(project)
    user_vote = Vote.objects.get_for_user(project, request.user)
    votes = Vote.objects.get_score(project)
    context = {
        'project': project,
        'votes': votes,
        'user_vote': user_vote,
        }
    return render(request, 'project/summary.html', context)


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


@login_required
def project_submission(request):
    """Handles project submissions"""
    if request.method == 'POST':
        form = ProjectSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.author = request.user
            instance.is_forkable = False
            instance.save()
            return HttpResponseRedirect(instance.get_absolute_url())
    else:
        form = ProjectSubmissionForm()
    context = {'form': form}
    return render(request, 'project/submission.html', context)


@login_required
def project_category_join(request, slug):
    category = get_object_or_404(ProjectCategory, slug=slug)
    membership_data = {
        'user': request.user.profile,
        'project_category': category,
        }
    try:
        membership = (ProjectCategoryMembership.objects.get(**membership_data))
        messages.error(request, _('You have previously sent this request'))
        return HttpResponseRedirect(reverse('users_dashboard'))
    except ProjectCategoryMembership.DoesNotExist:
        pass
    if request.method == 'POST':
        membership = (ProjectCategoryMembership.objects.create(**membership_data))
        messages.success(request, _('Your request has been sent'))
        context = {'membership': membership, 'SITE_URL': settings.SITE_URL,}
        subject = render_to_string('project/email/join_subject.txt', context)
        subject = ''.join(subject.splitlines())
        body = render_to_string('project/email/join_body.txt', context)
        notify_admins(subject, body)
        return HttpResponseRedirect(reverse('users_dashboard'))
    context = {'category': category}
    return render(request, 'project/join_category.html', context)


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


def get_template_or_404(slug):
    """Returns a template if avaliable, else 404"""
    try:
        template = Template.live.get(slug=slug)
    except Template.DoesNotExist:
        raise Http404
    return template


def template_detail(request, slug):
    template = get_template_or_404(slug)
    context = {'template': template,
               'project': None}
    return render(request, template.template, context)


def template_summary(request, slug):
    """Summary of a ``Template`` agregates metadata for the template"""
    template = get_template_or_404(slug)
    update_views_count(template)
    category_list = TemplateCategory.objects.filter(is_featured=True)
    project_list = Project.live.filter(template=template)[:5]
    tag_list = template.tags.all()
    user_vote = Vote.objects.get_for_user(template, request.user)
    votes = Vote.objects.get_score(template)
    context = {
        'template': template,
        'object': None,
        'category_list': category_list,
        'project_list': project_list,
        'tag_list': tag_list,
        'votes': votes,
        'user_vote': user_vote,
        }
    return render(request, 'template/object_detail.html', context)


def template_config(request, slug):
    template = get_template_or_404(slug)
    context = {'template': template,
               'object': None}
    return render(request, template.config, context)
