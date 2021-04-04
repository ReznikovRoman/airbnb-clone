from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User

from .forms import RealtyHostInlineFormSet, UserEditForm

# TODO: Complete Host views


class HostDetailsUpdateView(LoginRequiredMixin, generic.UpdateView):
    """Temporary View for updating host's details."""
    model = User
    form_class = UserEditForm
    template_name = 'hosts/host/form.html'
    success_url = reverse_lazy('home_page')

    login_url = reverse_lazy('home_page')  # TODO: edit login url (another issue)
    host_formset: RealtyHostInlineFormSet = None

    def get_object(self, queryset=None):
        return self.request.user

    def dispatch(self, request, *args, **kwargs):
        self.host_formset = RealtyHostInlineFormSet(self.request.POST or None, instance=self.get_object())
        return super(HostDetailsUpdateView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return self.render_to_response(
            context={
                'form': self.get_form(),
                'host_formset': self.host_formset,
            }
        )

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        user_form = self.get_form()
        host_formset = RealtyHostInlineFormSet(self.request.POST, instance=self.object)

        if user_form.is_valid():
            if host_formset.is_valid():
                host_formset.save()
                user_form.save()
                return redirect(self.success_url)

        return self.render_to_response(
            context={
                'form': user_form,
                'host_formset': host_formset,
            }
        )
