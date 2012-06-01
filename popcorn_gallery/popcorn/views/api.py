import json

from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST, require_GET
from django.http import HttpResponse, Http404, HttpResponseForbidden

from ..decorators import valid_user_project
from ..forms import ProjectForm
from ..models import Project
from ...base.decorators import json_handler, login_required_ajax


@require_GET
@login_required_ajax
def project_list(request):
    """List of the projects that belong to a User"""
    queryset = Project.objects.filter(~Q(status=Project.REMOVED),
                                      author=request.user)
    response = {
        'error': 'okay',
        'projects': [{'name': p.name, 'id': p.uuid} for p in queryset],
        }
    return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder),
                        mimetype='application/json')


def get_project_data(cleaned_data):
    return {
        'name': cleaned_data['name'],
        'metadata': cleaned_data['data'],
        'html': '',
        'template': cleaned_data['template'],
        }


@require_POST
@json_handler
@login_required_ajax
def project_add(request):
    """End point for adding a ``Project``"""
    form = ProjectForm(request.JSON)
    if form.is_valid():
        data = get_project_data(form.cleaned_data)
        data['author'] = request.user
        project = Project.objects.create(**data)
        response = {
            'error': 'okay',
            'project': project.butter_data,
            'url': project.get_absolute_url(),
            }
    else:
        response = {
            'error': 'error',
            'form_errors': form.errors
            }
    return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder),
                        mimetype='application/json')


@json_handler
@login_required_ajax
@valid_user_project(['uuid'])
def project_detail(request, project):
    """Handles the data for the Project"""
    if request.method == 'POST' and request.JSON:
        if project.author != request.user:
            if project.is_forkable:
                project = Project.objects.fork(project, request.user)
            else:
                return HttpResponseForbidden()
        form = ProjectForm(request.JSON)
        if form.is_valid():
            project.name = form.cleaned_data['name']
            project.metadata = form.cleaned_data['data']
            project.save()
            response = {
                'error': 'okay',
                'project': project.butter_data,
                'url': project.get_project_url(),
                }
        else:
            response = {
                'error': 'error',
                'form_errors': form.errors
                }
        return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder),
                            mimetype='application/json')
    response = {
        'error': 'okay',
        # Butter needs the project metadata as a string that can be
        # parsed to JSON
        'url': project.get_project_url(),
        'project': project.metadata,
        }
    return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder),
                        mimetype='application/json')


@json_handler
@login_required_ajax
def project_publish(request, uuid):
    if request.method == 'POST':
        try:
            project = Project.objects.get(~Q(status=Project.REMOVED),
                                          uuid=uuid, author=request.user)
        except Project.DoesNotExist:
            return HttpResponseForbidden()
        project.is_shared = True
        response = {
            'error': 'okay',
            'url': '%s%s' % (settings.SITE_URL, project.get_absolute_url()),
            }
        return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder),
                            mimetype='application/json')
    raise Http404


@login_required_ajax
def user_details(request):
    response = {
        'name': request.user.profile.display_name,
        'username': request.user.username,
        'email': request.user.email,
        }
    return HttpResponse(json.dumps(response, cls=DjangoJSONEncoder),
                        mimetype='application/json')
