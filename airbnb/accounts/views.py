from django.views import generic
from django.http import HttpRequest
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views

from .forms import SignUpForm


class SignUpView(generic.base.TemplateResponseMixin,
                 generic.View):
    """View for creating a new account."""
    form_class = SignUpForm
    template_name = 'accounts/registration/signup.html'

    def get(self, request: HttpRequest, *args, **kwargs):
        return self.render_to_response(
            context={
                'form': self.form_class(),
            }
        )

    def post(self, request: HttpRequest, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            user = form.save()
            # TODO: send an account verification link to the email (celery, another milestone)

            return redirect('accounts:login')

        return self.render_to_response(
            context={
                'form': form,
            }
        )


class CustomPasswordResetView(auth_views.PasswordResetView):
    """View for resetting a password."""
    template_name = 'accounts/registration/password_reset.html'
    success_url = reverse_lazy('accounts:password_reset_done')
    html_email_template_name = 'accounts/registration/password_reset_email.html'
    email_template_name = 'accounts/registration/password_reset_email.html'

    def get(self, request: HttpRequest, *args, **kwargs):
        print(request.get_host())
        return super(CustomPasswordResetView, self).get(request, *args, **kwargs)
