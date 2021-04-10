from django.http import HttpRequest
from django.shortcuts import redirect, reverse


class AnonymousUserRequiredMixin:
    """Verify that current user is not logged in."""
    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse('home_page'))
        return super(AnonymousUserRequiredMixin, self).dispatch(request, *args, **kwargs)
