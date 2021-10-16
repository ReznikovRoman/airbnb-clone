from django.urls import path

from . import views


app_name = 'subscribers'

urlpatterns = [
    path('new-subscription/', views.SubscribeView.as_view(), name='new_subscription'),
]
