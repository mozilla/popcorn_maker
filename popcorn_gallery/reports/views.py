from django.contrib import messages
from django.shortcuts import render, redirect
from django.template.loader import render_to_string

from tower import ugettext as _
from .forms import ReportForm
from ..base.utils import notify_admins
from ..base.decorators import throttle_view


@throttle_view(methods=['POST'], duration=30)
def report_form(request):
    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save()
            context = {'report': report}
            subject = render_to_string('reports/email_subject.txt', context)
            subject = ''.join(subject.splitlines())
            body = render_to_string('reports/email_body.txt', context)
            notify_admins(subject, body)
            messages.success(request, _('Report sent successfully'))
            return redirect('homepage')
    else:
        form = ReportForm()
    context = {'form': form}
    return render(request, 'reports/form.html', context)
