from django.contrib.sites.shortcuts import get_current_site
from django.views import generic
from django.http import HttpRequest
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404, reverse
from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin

from hosts.models import RealtyHost
from realty.models import CustomDeleteQueryset, Realty
from realty.services.realty import get_available_realty_by_host
from .forms import (SignUpForm, CustomPasswordResetForm,
                    ProfileForm, UserInfoForm, ProfileImageForm, ProfileDescriptionForm, VerificationCodeForm)
from .models import CustomUser, Profile
from .mixins import (AnonymousUserRequiredMixin, UnconfirmedPhoneNumberRequiredMixin, UnconfirmedEmailRequiredMixin,)
from .services import (get_user_from_uid, send_verification_link, handle_phone_number_change,
                       is_verification_code_for_profile_valid, set_profile_phone_number_confirmed,
                       get_verification_code_from_digits_dict)
from .tokens import account_activation_token


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
            send_verification_link(request, user)
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
    form_class = CustomPasswordResetForm


class AccountActivationView(generic.View):
    """View for confirming user's email."""
    def get(self, request: HttpRequest, uidb64, token, *args, **kwargs):
        try:
            user = get_user_from_uid(uidb64)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        if user is not None and account_activation_token.check_token(user, token):
            user.is_email_confirmed = True
            user.save()
            login(request, user)
            messages.add_message(request, messages.SUCCESS, message='You have successfully confirmed your email.')
            return redirect(reverse('home_page'))

        messages.add_message(request, messages.ERROR, message='There was an error while confirming your email.')
        return redirect(reverse('home_page'))


class ActivationRequiredView(generic.TemplateView):
    """Display error page - page requires confirmed email."""
    template_name = 'accounts/registration/account_activation_required.html'


class AccountSettingsDashboardView(LoginRequiredMixin,
                                   generic.TemplateView):
    """View for showing an account dashboard."""
    template_name = 'accounts/settings/settings_dashboard.html'


class PersonalInfoEditView(LoginRequiredMixin,
                           generic.base.TemplateResponseMixin,
                           generic.View):
    """View for editing user personal info."""
    template_name = 'accounts/settings/user_form.html'
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
            user: CustomUser = self.user_info_form.save()

            if 'email' in self.user_info_form.changed_data:
                messages.add_message(
                    request,
                    level=messages.SUCCESS,
                    message="We've sent a confirmation email to your email address"
                )
                user.is_email_confirmed = False
                user.save()
                send_verification_link(request, user)

        if self.profile_form.is_valid():
            user_profile: Profile = self.profile_form.save()
            profile_cleaned_data = self.profile_form.cleaned_data

            # if phone number has been changed
            if 'phone_number' in self.profile_form.changed_data:
                if profile_cleaned_data.get('phone_number', None):  # if it is not blank
                    messages.add_message(
                        request,
                        level=messages.SUCCESS,
                        message="We've sent a verification code to you. "
                                "You can confirm your phone number at the Login & Security panel."
                    )
                    handle_phone_number_change(
                        user_profile=user_profile,
                        site_domain=get_current_site(request).domain,
                        new_phone_number=str(profile_cleaned_data.get('phone_number')),
                    )
                else:
                    set_profile_phone_number_confirmed(user_profile, is_phone_number_confirmed=False)

            return redirect('accounts:user_info_edit')

        return self.render_to_response(
            context={
                'user_info_form': self.user_info_form,
                'profile_form': self.profile_form,
            }
        )


class ProfileShowView(generic.base.TemplateResponseMixin,
                      generic.View):
    """View for displaying a user profile."""
    template_name = 'accounts/profile/show.html'

    profile_owner: CustomUser = None
    is_profile_of_current_user: bool = False  # True if the profile is the current user's profile, False otherwise

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        self.profile_owner = get_object_or_404(CustomUser, pk=kwargs.get('user_pk'))

        if self.profile_owner == request.user:
            self.is_profile_of_current_user = True

        return super(ProfileShowView, self).dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, *args, **kwargs):
        host_listings: CustomDeleteQueryset[Realty] = Realty.available.none()
        if RealtyHost.objects.filter(user=self.profile_owner).exists():
            host_listings = get_available_realty_by_host(RealtyHost.objects.get(user=self.profile_owner))
        return self.render_to_response(
            context={
                'profile_owner': self.profile_owner,
                'is_profile_of_current_user': self.is_profile_of_current_user,
                'host_listings': host_listings,
            }
        )


class ProfileImageEditView(LoginRequiredMixin,
                           generic.base.TemplateResponseMixin,
                           generic.View):
    """View for editing a profile image."""
    template_name = 'accounts/profile/edit_image.html'

    profile_image_form: ProfileImageForm = None

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        self.profile_image_form = ProfileImageForm(
            data=request.POST or None,
            files=request.FILES or None,
            instance=request.user.profile,
        )
        return super(ProfileImageEditView, self).dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, *args, **kwargs):
        return self.render_to_response(
            context={
                'profile_image_form': self.profile_image_form,
            }
        )

    def post(self, request: HttpRequest, *args, **kwargs):
        if self.profile_image_form.is_valid():
            self.profile_image_form.save()
            return redirect(reverse('accounts:profile_show', kwargs={'user_pk': request.user.pk}))
        return self.render_to_response(
            context={
                'profile_image_form': self.profile_image_form,
            }
        )


class ProfileDescriptionEditView(LoginRequiredMixin,
                                 generic.base.TemplateResponseMixin,
                                 generic.View):
    """View for editing profile description."""
    template_name = 'accounts/profile/edit_description.html'

    profile_description_form: ProfileDescriptionForm = None

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        self.profile_description_form = ProfileDescriptionForm(
            data=request.POST or None,
            instance=request.user.profile,
        )
        return super(ProfileDescriptionEditView, self).dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, *args, **kwargs):
        return self.render_to_response(
            context={
                'profile_description_form': self.profile_description_form,
            }
        )

    def post(self, request: HttpRequest, *args, **kwargs):
        if self.profile_description_form.is_valid():
            self.profile_description_form.save()
            return redirect(reverse('accounts:profile_show', kwargs={'user_pk': request.user.pk}))
        return self.render_to_response(
            context={
                'profile_description_form': self.profile_description_form,
            }
        )


class SecurityDashboardView(LoginRequiredMixin,
                            generic.TemplateView):
    """View for showing a `Login & Security` dashboard."""
    template_name = 'accounts/settings/security_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(SecurityDashboardView, self).get_context_data(**kwargs)
        context['phone_number'] = self.request.user.profile.phone_number
        context['email'] = self.request.user.email
        return context


class PhoneNumberConfirmPageView(UnconfirmedPhoneNumberRequiredMixin,
                                 LoginRequiredMixin,
                                 generic.base.TemplateResponseMixin,
                                 generic.View):
    """View for confirming a phone number (by a verification SMS code)."""
    template_name = 'accounts/settings/confirm_phone.html'

    verification_code_form: VerificationCodeForm = None
    phone_number: str = None

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        self.verification_code_form = VerificationCodeForm(request.POST or None)
        self.phone_number = request.user.profile.phone_number
        return super(PhoneNumberConfirmPageView, self).dispatch(request, *args, **kwargs)
    
    def get(self, request: HttpRequest, *args, **kwargs):
        return self.render_to_response(
            context={
                'verification_code_form': self.verification_code_form,
                'phone_number': self.phone_number,
            }
        )

    def post(self, request: HttpRequest, *args, **kwargs):
        if self.verification_code_form.is_valid():
            if is_verification_code_for_profile_valid(
                    user_profile=request.user.profile,
                    verification_code=get_verification_code_from_digits_dict(self.verification_code_form.cleaned_data)
            ):
                set_profile_phone_number_confirmed(user_profile=request.user.profile)
                messages.add_message(
                    request,
                    level=messages.SUCCESS,
                    message='You have successfully confirmed your phone number'
                )
                return redirect(reverse('accounts:settings_dashboard'))
            else:
                messages.add_message(
                    request,
                    level=messages.ERROR,
                    message='Error: Your code is invalid'
                )

        return self.render_to_response(
            context={
                'verification_code_form': self.verification_code_form,
                'phone_number': self.phone_number,
            }
        )


class ConfirmEmailView(UnconfirmedEmailRequiredMixin,
                       LoginRequiredMixin,
                       generic.View):
    """View for sending a confirmation email to a user."""
    def get(self, request: HttpRequest, *args, **kwargs):
        send_verification_link(request, request.user)
        messages.add_message(
            request,
            level=messages.SUCCESS,
            message="We've sent a confirmation email to your email address"
        )
        return redirect(reverse('accounts:security_dashboard'))
