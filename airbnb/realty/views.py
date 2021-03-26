from django.views import generic

from .models import Realty


class RealtyListView(generic.ListView):
    """Display all realty objects"""
    model = Realty
    template_name = 'realty/realty/list.html'
