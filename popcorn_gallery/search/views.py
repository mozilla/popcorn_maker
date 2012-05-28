from .forms import SearchForm
from haystack.views import basic_search
from haystack.forms import SearchForm

def search(request):
    """Simple wrapper around the search"""
    return basic_search(request, form_class=SearchForm)
