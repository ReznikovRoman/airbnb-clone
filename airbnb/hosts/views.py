from django.http import HttpRequest
from django.views import generic
from django.shortcuts import redirect, reverse
from django.contrib.auth.mixins import LoginRequiredMixin

from accounts.mixins import ActivatedAccountRequiredMixin
from accounts.models import get_default_profile_image_full_url


class BecomeHostView(LoginRequiredMixin,
                     ActivatedAccountRequiredMixin,
                     generic.View):
    """View for handling new hosts."""
    def get(self, request: HttpRequest, *args, **kwargs):
        if request.user.profile.profile_image and \
                request.user.profile.profile_image.url != get_default_profile_image_full_url():
            return redirect(reverse('realty:new_realty'))
        else:
            return redirect(reverse('hosts:missing_image'))


class HostMissingImageView(LoginRequiredMixin,
                           ActivatedAccountRequiredMixin,
                           generic.TemplateView):
    """View for showing a 'missing profile image' error page."""
    template_name = 'hosts/host/missing_image.html'
