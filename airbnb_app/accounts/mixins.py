from typing import Union

from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpRequest
from django.shortcuts import redirect, reverse

from common.types import AuthenticatedHttpRequest

from .services import send_verification_link


class AnonymousUserRequiredMixin:
    """Verify that current user is not logged in."""

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse('home_page'))
        return super(AnonymousUserRequiredMixin, self).dispatch(request, *args, **kwargs)


class ActivatedAccountRequiredMixin:
    """Verify that current user has confirmed an email."""

    def dispatch(self, request: Union[HttpRequest, AuthenticatedHttpRequest], *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('accounts:login'))

        if not request.user.is_email_confirmed:
            send_verification_link(get_current_site(request).domain, request.scheme, request.user)
            return redirect(reverse('accounts:activation_required'))

        return super(ActivatedAccountRequiredMixin, self).dispatch(request, *args, **kwargs)


class UnconfirmedPhoneNumberRequiredMixin:
    """Verify that current user has not confirmed his phone number yet."""

    def dispatch(self, request: Union[HttpRequest, AuthenticatedHttpRequest], *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('accounts:login'))

        if (
                request.user.profile.is_phone_number_confirmed or
                request.user.profile.phone_number is None
        ):
            return redirect(reverse('accounts:settings_dashboard'))

        return super(UnconfirmedPhoneNumberRequiredMixin, self).dispatch(request, *args, **kwargs)


class UnconfirmedEmailRequiredMixin:
    """Verify that current user has not confirmed an email address yet."""

    def dispatch(self, request: Union[HttpRequest, AuthenticatedHttpRequest], *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(reverse('accounts:login'))

        if request.user.is_email_confirmed:
            return redirect(reverse('accounts:settings_dashboard'))

        return super(UnconfirmedEmailRequiredMixin, self).dispatch(request, *args, **kwargs)
