from django.urls import path

from . import views


app_name = 'hosts'

urlpatterns = [
    path('become-a-host/', views.BecomeHostView.as_view(), name='become_a_host'),
    path('become-a-host/missing-image/', views.HostMissingImageView.as_view(), name='missing_image'),
]
