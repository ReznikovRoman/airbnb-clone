from django.urls import path

from . import views


app_name = 'realty'

urlpatterns = [
    path('', views.RealtyListView.as_view(), name='all'),
    path('rooms/<slug>/', views.RealtyDetailView.as_view(), name='detail'),
    path('<slug:city_slug>/', views.RealtyListView.as_view(), name='all_by_city'),
]

