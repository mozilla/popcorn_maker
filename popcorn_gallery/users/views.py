import jingo

from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render

from django_extensions.db.fields import json
from django_browserid.views import Verify
from funfactory.urlresolvers import reverse
from tower import ugettext as _

from .models import Profile
from .forms import ProfileCreateForm, ProfileForm
from ..popcorn.models import Project
from ..activity.models import Activity


class AjaxVerify(Verify):
    """Handles AJAX requests for ``browserid``.
    If requested via ajax will return json.
    On success returns with the status code ``200`` with the
    following details::

    {
        'status: 'okay',
        'email': 'USER_EMAIL_ADDRESS',
    }

    On failure it will return with the status code ``200`` with the
    following details::

    {
        'status': 'failed'
    }
    """

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
        super(AjaxVerify, self).login_failure()
        if self.request.is_ajax():
            return HttpResponse(json.dumps({'status': 'failed'}),
                                mimetype='application/json')
        return redirect('login_failed')


@login_required
def dashboard(request):
    """Display first page of activities for a users dashboard."""
    user_profile = request.user.get_profile()
    project_list = Project.objects.get_for_user(request.user)
    activity_list = Activity.objects.get_for_user(request.user)[:5]
    context = {
        'profile': user_profile,
        'project_list': project_list,
        'activity_list': activity_list,
        }
    return jingo.render(request, 'users/dashboard.html', context)


def signout(request):
    """Sign the user out, destroying their session."""
    auth.logout(request)
    if request.is_ajax():
        return HttpResponse('{"error": "okay"}', 'application/javascript')
    return redirect('/')


def profile(request, username):
    """Display profile page for user specified by ``username``."""
    try:
        profile = Profile.objects.get(user__username=username)
    except Profile.DoesNotExist:
        raise Http404
    # If the identifier hasn't been chosen that means the user hasn't
    # accepted the Terms and Conditions
    if not profile.has_chosen_identifier:
        raise Http404
    if request.user == profile.user:
        project_list = Project.objects.get_for_user(request.user)
    else:
        project_list = Project.live.filter(author=profile.user)
    activity_list = Activity.objects.get_for_user(profile.user)[:5]
    context = {
        'profile': profile,
        'project_list': project_list,
        'activity_list': activity_list,
        }
    return jingo.render(request, 'users/profile.html', context)


@login_required
def edit(request, template='users/edit.html'):
    """Edit the currently logged in users profile.
    Creates one if the profile is missing"""
    try:
        profile = request.user.get_profile()
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)
    ProfileFormClass = ProfileForm
    mode = 'edit'
    if not profile.has_chosen_identifier:
        mode = 'create'
        ProfileFormClass = ProfileCreateForm
    if request.method == 'POST':
        form = ProfileFormClass(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save()
            if mode == 'create':
                profile.user.username = form.cleaned_data['username']
                profile.user.save()
            return redirect(profile.get_absolute_url())
    else:
        form = ProfileFormClass(instance=profile)
    context = {
        'form': form,
        'profile': profile,
        'page_mode': mode,
        }
    return jingo.render(request, template, context)


@login_required
def delete_profile(request, template='users/profile_confirm_delete.html'):
    profile = get_object_or_404(Profile, user=request.user)
    if request.method == 'POST':
        Project.objects.filter(author=request.user).delete()
        profile.delete()
        request.user.delete()
        auth.logout(request)
        messages.success(request, _(u'Your profile was successfully deleted.'))
        return redirect(reverse('homepage'))
    context = {'profile': profile}
    return jingo.render(request, template, context)


def login(request, failed=False):
    """Error message when the authentication failed"""
    if request.user.is_authenticated():
        return redirect('users_dashboard')
    context = {'failed': failed}
    return render(request, 'login.html', context)
