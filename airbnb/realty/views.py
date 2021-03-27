from django.views import generic

from .models import Realty
from .forms import RealtyTypeForm


class RealtyListView(generic.ListView):
    """Display all realty objects"""
    model = Realty
    template_name = 'realty/realty/list.html'
    paginate_by = 3
    realty_type_form = None

    def dispatch(self, request, *args, **kwargs):
        # TODO: get initial form data from session
        self.realty_type_form = RealtyTypeForm()
        return super(RealtyListView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        available_realty = Realty.available.all()

        city_slug = self.kwargs.get('city_slug', None)
        if city_slug:
            available_realty = available_realty.filter(location__city_slug=city_slug)

        realty_types = self.request.GET.getlist('realty_type', None)
        if realty_types:
            available_realty = available_realty.filter(realty_type__in=realty_types)

        return available_realty

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(RealtyListView, self).get_context_data(**kwargs)
        context['realty_count'] = self.get_queryset().count()

        city_slug = self.kwargs.get('city_slug', 'All cities')
        context['city'] = city_slug.capitalize()

        context['realty_type_form'] = self.realty_type_form
        return context


class RealtyDetailView(generic.DetailView):
    """Display single Realty"""
    model = Realty
    template_name = 'realty/realty/detail.html'
