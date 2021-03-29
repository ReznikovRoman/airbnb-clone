from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import HostDetailsForm
from .models import RealtyHost

# TODO: Complete Host views


class HostDetailsUpdateView(LoginRequiredMixin, generic.UpdateView):
    """Temporary View for updating host's details."""
    model = RealtyHost
    form_class = HostDetailsForm
    template_name = 'hosts/host/form.html'
    success_url = reverse_lazy('home_page')

    def get_object(self, queryset=None):
        return get_object_or_404(RealtyHost, user=self.request.user)
