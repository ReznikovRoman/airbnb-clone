from django.views import generic
from django.http import HttpRequest
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import SignUpForm, ProfileForm, UserInfoForm
from .models import CustomUser, Profile
from .mixins import AnonymousUserRequiredMixin


class SignUpView(AnonymousUserRequiredMixin,
                 generic.base.TemplateResponseMixin,
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
            # TODO: send an account verification link to the email

            return redirect('accounts:login')

        return self.render_to_response(
            context={
                'form': form,
            }
        )


class LoginView(AnonymousUserRequiredMixin,
                auth_views.LoginView):
    """View for signing in."""
    template_name = 'accounts/registration/login.html'


class CustomPasswordResetView(auth_views.PasswordResetView):
    """View for resetting a password."""
    template_name = 'accounts/registration/password_reset.html'
    success_url = reverse_lazy('accounts:password_reset_done')
    html_email_template_name = 'accounts/registration/password_reset_email.html'
    email_template_name = 'accounts/registration/password_reset_email.html'

    def get(self, request: HttpRequest, *args, **kwargs):
        return super(CustomPasswordResetView, self).get(request, *args, **kwargs)


class AccountSettingsDashboardView(LoginRequiredMixin,
                                   generic.TemplateView):
    """View for showing an account dashboard."""
    template_name = 'accounts/settings_dashboard.html'


class PersonalInfoEditView(LoginRequiredMixin,
                           generic.base.TemplateResponseMixin,
                           generic.View):
    """View for editing user personal info."""
    template_name = 'accounts/user_form.html'
    profile_form: ProfileForm = None
    user_info_form: UserInfoForm = None

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        self.profile_form = ProfileForm(
            data=request.POST or None,
            files=request.FILES or None,
            instance=request.user.profile,
        )
        self.user_info_form = UserInfoForm(
            data=request.POST or None,
            instance=request.user,
        )
        return super(PersonalInfoEditView, self).dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, *args, **kwargs):
        return self.render_to_response(
            context={
                'user_info_form': self.user_info_form,
                'profile_form': self.profile_form,
            }
        )

    def post(self, request: HttpRequest, *args, **kwargs):
        if self.user_info_form.is_valid():
            user_info: CustomUser = self.user_info_form.save()
        if self.profile_form.is_valid():
            user_profile: Profile = self.profile_form.save()
            return redirect('accounts:user_info_edit')

        return self.render_to_response(
            context={
                'user_info_form': self.user_info_form,
                'profile_form': self.profile_form,
            }
        )
