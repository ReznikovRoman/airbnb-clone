from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, reverse
from django.views import generic

from accounts.mixins import ActivatedAccountRequiredMixin
from accounts.services import has_user_profile_image
from common.types import AuthenticatedHttpRequest


class BecomeHostView(LoginRequiredMixin,
                     ActivatedAccountRequiredMixin,
                     generic.View):
    """View for handling new hosts."""

    def get(self, request: AuthenticatedHttpRequest, *args, **kwargs):
        if has_user_profile_image(user_profile=request.user.profile):
            return redirect(reverse('realty:new_realty'))
        else:
            return redirect(reverse('hosts:missing_image'))


class HostMissingImageView(LoginRequiredMixin,
                           ActivatedAccountRequiredMixin,
                           generic.TemplateView):
    """View for showing a 'missing profile image' error page."""

    template_name = 'hosts/host/missing_image.html'
