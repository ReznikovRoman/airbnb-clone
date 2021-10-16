from django.db.models import QuerySet
from django.shortcuts import render
from django.views import generic

from .constants import DISPLAYED_CITIES_COUNT
from .services import get_all_realty_cities


class HomePageView(generic.TemplateView):
    """Display home page."""

    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)

        # TODO: get most popular cities (by views + booking count, - Redis, sorted set (another milestone)
        context['popular_cities']: QuerySet = get_all_realty_cities()[:DISPLAYED_CITIES_COUNT]
        context['meta_description'] = "Find vacation rentals, cabins, beach houses, " \
                                      "unique homes and experiences around the world - " \
                                      "all made possible by hosts on Airbnb."

        return context


class RobotsView(generic.TemplateView):
    """Display `robots.txt` file."""

    template_name = 'main/robots.txt'
    content_type = 'text/plain'


def bad_request_view(request, *args, **kwargs):
    response = render(request, 'main/errors/400.html')
    response.status_code = 400
    return response


def permission_denied_view(request, *args, **kwargs):
    response = render(request, 'main/errors/403.html')
    response.status_code = 403
    return response


def page_not_found_view(request, *args, **kwargs):
    response = render(request, 'main/errors/404.html')
    response.status_code = 404
    return response


def server_error_view(request, *args, **kwargs):
    response = render(request, 'main/errors/500.html')
    response.status_code = 500
    return response
