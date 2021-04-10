from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views

from . import views


app_name = 'accounts'

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('login/',
         views.LoginView.as_view(),
         name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('personal-info/', views.UserInfoEditView.as_view(), name='user_info_edit'),

    # password change urls
    path('password_change/',
         auth_views.PasswordChangeView.as_view(
             template_name='accounts/registration/password_change.html',
             success_url=reverse_lazy('accounts:password_change_done'),
         ),
         name='password_change'),
    path('password_change/done/',
         auth_views.PasswordChangeDoneView.as_view(template_name='accounts/registration/password_change_done.html'),
         name='password_change_done'),

    # password reset urls
    path('password_reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='accounts/registration/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='accounts/registration/password_reset_confirm.html',
             success_url=reverse_lazy('accounts:password_reset_complete'),
         ),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='accounts/registration/password_reset_complete.html'
         ),
         name='password_reset_complete'),
]
