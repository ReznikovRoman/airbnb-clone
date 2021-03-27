from django.views import generic

from .models import Realty


class RealtyListView(generic.ListView):
    """Display all realty objects"""
    model = Realty
    template_name = 'realty/realty/list.html'
    paginate_by = 3
    queryset = Realty.available.all()

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super(RealtyListView, self).get_context_data(**kwargs)
        context['realty_count'] = self.queryset.count()
        return context


class RealtyDetailView(generic.DetailView):
    """Display single Realty"""
    model = Realty
    template_name = 'realty/realty/detail.html'
