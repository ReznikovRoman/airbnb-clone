from django.urls import path

from . import views


app_name = 'realty'

urlpatterns = [
    path('', views.RealtyListView.as_view(), name='all'),
]

