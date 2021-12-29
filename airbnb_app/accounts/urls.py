from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views


app_name = 'accounts'

urlpatterns = [
    path(
        route='signup/',
        view=views.SignUpView.as_view(),
        name='signup',
    ),
    path(
        route='login/',
        view=views.LoginView.as_view(),
        name='login',
    ),
    path(
        route='logout/',
        view=auth_views.LogoutView.as_view(),
        name='logout',
    ),
    path('activate/<uidb64>/<token>/', views.AccountActivationView.as_view(), name='activate'),
    path('activation-required/', views.ActivationRequiredView.as_view(), name='activation_required'),

    path('settings/', views.AccountSettingsDashboardView.as_view(), name='settings_dashboard'),
    path('settings/personal-info/', views.PersonalInfoEditView.as_view(), name='user_info_edit'),

    path('settings/login-and-security/', views.SecurityDashboardView.as_view(), name='security_dashboard'),
    path(
        route='settings/login-and-security/confirm-phone/',
        view=views.PhoneNumberConfirmPageView.as_view(),
        name='confirm_phone',
    ),
    path('settings/login-and-security/confirm-email/', views.SendConfirmationEmailView.as_view(), name='confirm_email'),

    path('show/<int:user_pk>/', views.ProfileShowView.as_view(), name='profile_show'),
    path('edit-image/', views.ProfileImageEditView.as_view(), name='edit_image'),
    path('edit-description/', views.ProfileDescriptionEditView.as_view(), name='edit_description'),

    # password change urls
    path(
        route='password_change/',
        view=auth_views.PasswordChangeView.as_view(
            template_name='accounts/registration/password_change.html',
            success_url=reverse_lazy('accounts:password_change_done'),
         ),
        name='password_change',
    ),
    path(
        route='password_change/done/',
        view=auth_views.PasswordChangeDoneView.as_view(template_name='accounts/registration/password_change_done.html'),
        name='password_change_done',
    ),

    # password reset urls
    path('password_reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path(
        route='password_reset/done/',
        view=auth_views.PasswordResetDoneView.as_view(template_name='accounts/registration/password_reset_done.html'),
        name='password_reset_done',
    ),
    path(
        route='reset/<uidb64>/<token>/',
        view=auth_views.PasswordResetConfirmView.as_view(
            template_name='accounts/registration/password_reset_confirm.html',
            success_url=reverse_lazy('accounts:password_reset_complete'),
         ),
        name='password_reset_confirm',
    ),
    path(
        route='reset/done/',
        view=auth_views.PasswordResetCompleteView.as_view(
            template_name='accounts/registration/password_reset_complete.html',
         ),
        name='password_reset_complete',
    ),
]
