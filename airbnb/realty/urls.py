from django.urls import path

from . import views


app_name = 'realty'

urlpatterns = [
    path('', views.RealtyListView.as_view(), name='all'),
    path('rooms/<slug>/', views.RealtyDetailView.as_view(), name='detail'),

    # Edit realty
    path('new/', views.RealtyEditView.as_view(), name='new_realty'),
    path('<int:realty_id>/edit/', views.RealtyEditView.as_view(), name='edit_realty'),

    # Images
    path('image/order/', views.RealtyImageOrderView.as_view(), name='image_change_order'),

    path('<slug:city_slug>/', views.RealtyListView.as_view(), name='all_by_city'),
]

