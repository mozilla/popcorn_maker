from django.http import Http404
from django.shortcuts import render
from haystack.query import EmptySearchQuerySet, SearchQuerySet

from .forms import SearchForm
from ..popcorn.models import Project, Template


def search(request):
    """Simple search returns two separate querysets for
     - ``popcorn.project``
     - ``popcorn.template``
    """
    query = ''
    template_results = EmptySearchQuerySet()
    project_results = EmptySearchQuerySet()
    form = SearchForm()
    if request.GET.get('q'):
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['q']
            project_results = (SearchQuerySet().auto_query(query)
                               .models(Project))
            template_results = (SearchQuerySet().auto_query(query)
                                .models(Template))
    context = {
        'form': form,
        'query': query,
        'suggestion': None,
        'template_results': template_results,
        'project_results': project_results,
    }
    if template_results.query.backend.include_spelling:
        context['suggestion'] = form.get_suggestion()
    return render(request, 'search/search.html', context)
