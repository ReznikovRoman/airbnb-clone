from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpRequest
from django.shortcuts import redirect, reverse
from django.urls import reverse_lazy
from django.views import generic

from common.constants import (
    TWILIO_MESSAGE_STATUS_CODES_FAILED, VERIFICATION_CODE_STATUS_DELIVERED, VERIFICATION_CODE_STATUS_FAILED,
)
from common.types import AuthenticatedHttpRequest
from hosts.services import get_host_or_none_by_user
from realty.services.realty import get_available_realty_by_host

from .constants import (
    EMAIL_CONFIRMATION_FAILURE_RESPONSE_MESSAGE, EMAIL_CONFIRMATION_SUCCESS_RESPONSE_MESSAGE,
    EMAIL_SENT_SUCCESSFULLY_RESPONSE_MESSAGE, PHONE_NUMBER_CONFIRMATION_SUCCESS_RESPONSE_MESSAGE,
    PROFILE_INFO_EDIT_SUCCESS_RESPONSE_MESSAGE, SMS_CODE_INVALID_RESPONSE_MESSAGE, SMS_NOT_DELIVERED_RESPONSE_MESSAGE,
    SMS_SENT_SUCCESSFULLY_RESPONSE_MESSAGE,
)
from .forms import (
    CustomPasswordResetForm, ProfileDescriptionForm, ProfileForm, ProfileImageForm, SignUpForm, UserInfoForm,
    VerificationCodeForm,
)
from .mixins import AnonymousUserRequiredMixin, UnconfirmedEmailRequiredMixin, UnconfirmedPhoneNumberRequiredMixin
from .models import CustomUser, Profile
from .services import (
    create_jwt_token_for_user_with_additional_fields, get_phone_code_status_by_user_id, get_user_by_pk,
    get_user_from_uid, get_verification_code_from_digits_dict, handle_phone_number_change,
    is_verification_code_for_profile_valid, send_verification_link, set_phone_code_status_by_user_id,
    update_phone_number_confirmation_status, update_user_email_confirmation_status,
)
from .tokens import account_activation_token


class SignUpView(
    AnonymousUserRequiredMixin,
    generic.base.TemplateResponseMixin,
    generic.View,
):
    """View for creating a new account."""

    form_class = SignUpForm
    template_name = 'accounts/registration/signup.html'

    def get(self, request: HttpRequest, *args, **kwargs):
        return self.render_to_response(
            context={
                'form': self.form_class(),
            },
        )

    def post(self, request: HttpRequest, *args, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            user = form.save()
            create_jwt_token_for_user_with_additional_fields(user=user)
            send_verification_link(get_current_site(request).domain, request.scheme, user)
            return redirect('accounts:login')

        return self.render_to_response(
            context={
                'form': form,
            },
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
            user = update_user_email_confirmation_status(user=user, is_email_confirmed=True)
            create_jwt_token_for_user_with_additional_fields(user=user)
            login(request, user)
            messages.add_message(request, messages.SUCCESS, EMAIL_CONFIRMATION_SUCCESS_RESPONSE_MESSAGE)
            return redirect(reverse('home_page'))

        messages.add_message(request, messages.ERROR, EMAIL_CONFIRMATION_FAILURE_RESPONSE_MESSAGE)
        return redirect(reverse('home_page'))


class ActivationRequiredView(generic.TemplateView):
    """Display error page - page requires confirmed email."""

    template_name = 'accounts/registration/account_activation_required.html'


class AccountSettingsDashboardView(
    LoginRequiredMixin,
    generic.TemplateView,
):
    """View for showing an account dashboard."""

    template_name = 'accounts/settings/settings_dashboard.html'


class PersonalInfoEditView(
    LoginRequiredMixin,
    generic.base.TemplateResponseMixin,
    generic.View,
):
    """View for editing user personal info."""

    template_name = 'accounts/settings/user_form.html'
    profile_form: ProfileForm = None
    user_info_form: UserInfoForm = None

    def dispatch(self, request: AuthenticatedHttpRequest, *args, **kwargs):
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
            },
        )

    def post(self, request: HttpRequest, *args, **kwargs):
        if self.user_info_form.is_valid() and self.profile_form.is_valid():
            user: CustomUser = self.user_info_form.save()
            user_profile: Profile = self.profile_form.save()
            profile_cleaned_data = self.profile_form.cleaned_data
            user_id = self.request.user.id

            # if email has been changed
            if 'email' in self.user_info_form.changed_data:
                messages.add_message(request, messages.SUCCESS, EMAIL_SENT_SUCCESSFULLY_RESPONSE_MESSAGE)
                update_user_email_confirmation_status(user, is_email_confirmed=False)
                send_verification_link(get_current_site(request).domain, request.scheme, user)

            # if phone number has been changed or verification code hasn't been delivered
            if (
                    'phone_number' in self.profile_form.changed_data or
                    get_phone_code_status_by_user_id(user_id) == VERIFICATION_CODE_STATUS_FAILED
            ):
                if profile_cleaned_data.get('phone_number', None):  # if it is not blank
                    twilio_payload = handle_phone_number_change(
                        user_profile=user_profile,
                        site_domain=get_current_site(request).domain,
                        new_phone_number=str(profile_cleaned_data.get('phone_number')),
                    )

                    # if SMS code hasn't been sent yet
                    failed_status_codes = (TWILIO_MESSAGE_STATUS_CODES_FAILED, VERIFICATION_CODE_STATUS_FAILED)
                    if twilio_payload.status.lower() in failed_status_codes:
                        set_phone_code_status_by_user_id(
                            user_id=user_id,
                            phone_code_status=VERIFICATION_CODE_STATUS_FAILED,
                        )
                        messages.add_message(request, messages.ERROR, SMS_NOT_DELIVERED_RESPONSE_MESSAGE)
                    else:
                        set_phone_code_status_by_user_id(
                            user_id=user_id,
                            phone_code_status=VERIFICATION_CODE_STATUS_DELIVERED,
                        )
                        messages.add_message(request, messages.SUCCESS, SMS_SENT_SUCCESSFULLY_RESPONSE_MESSAGE)
                else:  # if phone number has been removed
                    update_phone_number_confirmation_status(user_profile, is_phone_number_confirmed=False)

            if self.profile_form.changed_data or self.user_info_form.changed_data:
                messages.add_message(request, messages.SUCCESS, PROFILE_INFO_EDIT_SUCCESS_RESPONSE_MESSAGE)
            return redirect('accounts:user_info_edit')

        return self.render_to_response(
            context={
                'user_info_form': self.user_info_form,
                'profile_form': self.profile_form,
            },
        )


class ProfileShowView(
    generic.base.TemplateResponseMixin,
    generic.View,
):
    """View for displaying a user profile."""

    template_name = 'accounts/profile/show.html'

    profile_owner: CustomUser = None
    is_profile_of_current_user: bool = False  # True if the profile is the current user's profile, False otherwise

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        self.profile_owner = get_user_by_pk(pk=kwargs.get('user_pk'))

        if self.profile_owner == request.user:
            self.is_profile_of_current_user = True

        return super(ProfileShowView, self).dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, *args, **kwargs):
        host_listings = get_available_realty_by_host(
            realty_host=get_host_or_none_by_user(user=self.profile_owner),
        )

        return self.render_to_response(
            context={
                'profile_owner': self.profile_owner,
                'is_profile_of_current_user': self.is_profile_of_current_user,
                'host_listings': host_listings,
            },
        )


class ProfileImageEditView(
    LoginRequiredMixin,
    generic.base.TemplateResponseMixin,
    generic.View,
):
    """View for editing a profile image."""

    template_name = 'accounts/profile/edit_image.html'

    profile_image_form: ProfileImageForm = None

    def dispatch(self, request: AuthenticatedHttpRequest, *args, **kwargs):
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
            },
        )

    def post(self, request: HttpRequest, *args, **kwargs):
        if self.profile_image_form.is_valid():
            self.profile_image_form.save()
            return redirect(reverse('accounts:profile_show', kwargs={'user_pk': request.user.pk}))
        return self.render_to_response(
            context={
                'profile_image_form': self.profile_image_form,
            },
        )


class ProfileDescriptionEditView(
    LoginRequiredMixin,
    generic.base.TemplateResponseMixin,
    generic.View,
):
    """View for editing profile description."""

    template_name = 'accounts/profile/edit_description.html'

    profile_description_form: ProfileDescriptionForm = None

    def dispatch(self, request: AuthenticatedHttpRequest, *args, **kwargs):
        self.profile_description_form = ProfileDescriptionForm(
            data=request.POST or None,
            instance=request.user.profile,
        )
        return super(ProfileDescriptionEditView, self).dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest, *args, **kwargs):
        return self.render_to_response(
            context={
                'profile_description_form': self.profile_description_form,
            },
        )

    def post(self, request: HttpRequest, *args, **kwargs):
        if self.profile_description_form.is_valid():
            self.profile_description_form.save()
            return redirect(reverse('accounts:profile_show', kwargs={'user_pk': request.user.pk}))
        return self.render_to_response(
            context={
                'profile_description_form': self.profile_description_form,
            },
        )


class SecurityDashboardView(
    LoginRequiredMixin,
    generic.TemplateView,
):
    """View for showing a `Login & Security` dashboard."""

    template_name = 'accounts/settings/security_dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(SecurityDashboardView, self).get_context_data(**kwargs)
        context['phone_number'] = self.request.user.profile.phone_number
        context['email'] = self.request.user.email
        return context


class PhoneNumberConfirmPageView(
    UnconfirmedPhoneNumberRequiredMixin,
    LoginRequiredMixin,
    generic.base.TemplateResponseMixin,
    generic.View,
):
    """View for confirming a phone number (by a verification SMS code)."""

    template_name = 'accounts/settings/confirm_phone.html'

    verification_code_form: VerificationCodeForm = None
    is_verification_code_sent: bool = False

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        self.verification_code_form = VerificationCodeForm(request.POST or None)

        if get_phone_code_status_by_user_id(self.request.user.id) == VERIFICATION_CODE_STATUS_DELIVERED:
            self.is_verification_code_sent = True
        else:
            self.is_verification_code_sent = False

        return super(PhoneNumberConfirmPageView, self).dispatch(request, *args, **kwargs)

    def get(self, request: AuthenticatedHttpRequest, *args, **kwargs):
        return self.render_to_response(
            context={
                'verification_code_form': self.verification_code_form,
                'is_verification_code_sent': self.is_verification_code_sent,
            },
        )

    def post(self, request: AuthenticatedHttpRequest, *args, **kwargs):
        if self.verification_code_form.is_valid():
            if is_verification_code_for_profile_valid(
                    user_profile=request.user.profile,
                    verification_code=get_verification_code_from_digits_dict(self.verification_code_form.cleaned_data),
            ):
                update_phone_number_confirmation_status(request.user.profile, is_phone_number_confirmed=True)
                messages.add_message(request, messages.SUCCESS, PHONE_NUMBER_CONFIRMATION_SUCCESS_RESPONSE_MESSAGE)
                return redirect(reverse('accounts:settings_dashboard'))
            else:
                messages.add_message(request, messages.ERROR, SMS_CODE_INVALID_RESPONSE_MESSAGE)

        return self.render_to_response(
            context={
                'verification_code_form': self.verification_code_form,
                'is_verification_code_sent': self.is_verification_code_sent,
            },
        )


class SendConfirmationEmailView(
    UnconfirmedEmailRequiredMixin,
    LoginRequiredMixin,
    generic.View,
):
    """View for sending a confirmation email to a user."""

    def get(self, request: AuthenticatedHttpRequest, *args, **kwargs):
        send_verification_link(get_current_site(request).domain, request.scheme, request.user)
        messages.add_message(request, messages.SUCCESS, EMAIL_SENT_SUCCESSFULLY_RESPONSE_MESSAGE)
        return redirect(reverse('accounts:security_dashboard'))
