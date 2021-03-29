from django.views import generic
from django.db.models import QuerySet

from .services import get_all_realty_cities
from .constants import DISPLAYED_CITIES_COUNT


class HomePageView(generic.TemplateView):
    """Display home page"""
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)

        # TODO: get most popular cities (by views, о - Redis, sorted set (another milestone)
        context['popular_cities']: QuerySet = get_all_realty_cities()[:DISPLAYED_CITIES_COUNT]
        return context
