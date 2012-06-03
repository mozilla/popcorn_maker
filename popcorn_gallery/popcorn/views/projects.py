import json
import re

from functools import partial

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.utils.encoding import smart_unicode

from funfactory.urlresolvers import reverse
from tower import ugettext as _
from voting.models import Vote

from ..decorators import (valid_user_project, is_popcorn_project,
                          add_csrf_token)
from ..forms import (ProjectEditForm, ExternalProjectEditForm,
                     ProjectSubmissionForm, OrderingForm)
from ..models import (Project, ProjectCategory, Template, TemplateCategory,
                      ProjectCategoryMembership)
from ..utils import update_views_count, get_order_fields, update_vote_score
from ...base.utils import notify_admins


# default arguments for the project view
project_view = partial(valid_user_project(['username', 'shortcode']))


@project_view
@is_popcorn_project
@add_csrf_token
def user_project(request, project):
    context = {'project': project, 'template': project.template}
    return HttpResponse(smart_unicode(project.template.template_content))


@project_view
@is_popcorn_project
def user_project_config(request, project):
    return template_config_response(project.template)


@project_view
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


@project_view
@is_popcorn_project
def user_project_data(request, project):
    response = project.metadata if project.metadata else "{}"
    return HttpResponse(response, mimetype='application/json')


@login_required
@project_view
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
@project_view
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
@project_view
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


@project_view
def user_project_summary(request, project):
    update_views_count(project)
    user_vote = Vote.objects.get_for_user(project, request.user)
    votes = update_vote_score(project)
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
    order_fields = get_order_fields(request.GET)
    object_list = (Project.live.filter(**kwargs)
                   .order_by(*order_fields))
    category_list = ProjectCategory.objects.filter(is_featured=True)
    order_form = OrderingForm()
    context = {
        'category': category,
        'project_list': object_list,
        'category_list': category_list,
        'order_form': order_form
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
        messages.success(request, _(u'Your request has been sent'))
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
    order_fields = get_order_fields(request.GET)
    object_list = (Template.live.filter(**kwargs)
                   .order_by(*order_fields))
    category_list = TemplateCategory.objects.filter(is_featured=True)
    order_form = OrderingForm()
    context = {
        'template_list': object_list,
        'category': category,
        'category_list': category_list,
        'order_form': order_form,
        }
    return render(request, 'template/object_list.html', context)


def get_template_or_404(slug):
    """Returns a template if avaliable, else 404"""
    try:
        template = Template.live.get(slug=slug)
    except Template.DoesNotExist:
        raise Http404
    return template


@add_csrf_token
def template_detail(request, slug):
    template = get_template_or_404(slug)
    return HttpResponse(smart_unicode(template.template_content))


def template_summary(request, slug):
    """Summary of a ``Template`` agregates metadata for the template"""
    template = get_template_or_404(slug)
    update_views_count(template)
    category_list = TemplateCategory.objects.filter(is_featured=True)
    project_list = Project.live.filter(template=template)[:5]
    tag_list = template.tags.all()
    user_vote = Vote.objects.get_for_user(template, request.user)
    votes = update_vote_score(template)
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
    """Initialization data ``Template`` specific"""
    template = get_template_or_404(slug)
    return template_config_response(template)


def template_config_response(template):
    """Generates a valid response for a template config """
    data = {
        "savedDataUrl": "data",
        "baseDir": settings.STATIC_URL,
        "name": template.slug,
        }
    if template.config:
        data.update(template.config)
    return HttpResponse(json.dumps(data), mimetype='application/json')


def template_metadata(request, slug):
    template = get_template_or_404(slug)
    response = template.metadata if template.metadata else "{}"
    return HttpResponse(response, mimetype='application/json')
