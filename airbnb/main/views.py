from django.views import generic

from .services import get_all_realty_cities


class HomePageView(generic.TemplateView):
    """Display home page"""
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super(HomePageView, self).get_context_data(**kwargs)
        context['cities'] = get_all_realty_cities()
        return context
