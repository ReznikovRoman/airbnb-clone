from django.urls import path

from . import views


app_name = 'realty'

urlpatterns = [
    path('rooms/<slug>/', views.RealtyDetailView.as_view(), name='detail'),
    path('', views.RealtyListView.as_view(), name='all'),
]

