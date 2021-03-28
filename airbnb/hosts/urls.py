from django.urls import path

from . import views


app_name = 'hosts'

urlpatterns = [
    path('profile/edit/', views.HostDetailsUpdateView.as_view(), name='details_update'),
]
