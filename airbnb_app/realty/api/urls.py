from django.urls import path

from . import views


app_name = 'realty'

urlpatterns = [
    path('realty/', views.RealtyListApiView.as_view(), name='realty_list'),
    path('realty/<int:pk>/', views.RealtyDetailApiView.as_view(), name='realty_detail'),
]
