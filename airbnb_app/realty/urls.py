from django.urls import path
from django.contrib.sitemaps.views import sitemap

from . import views
from .sitemaps import RealtySiteMap


sitemaps = {
    'realty': RealtySiteMap,
}

app_name = 'realty'

urlpatterns = [
    path('', views.RealtyListView.as_view(), name='all'),
    path('search/', views.RealtySearchResultsView.as_view(), name='search'),
    path('rooms/<int:pk>/<slug>/', views.RealtyDetailView.as_view(), name='detail'),
    path('city/<slug:city_slug>/', views.RealtyListView.as_view(), name='all_by_city'),

    # Edit realty
    path('new/', views.RealtyEditView.as_view(), name='new_realty'),
    path('<int:realty_id>/edit/', views.RealtyEditView.as_view(), name='edit_realty'),

    # Realty - steps
    path('new/info/', views.RealtyGeneralInfoEditView.as_view(), name='new_realty_info'),
    path('new/location/', views.RealtyLocationEditView.as_view(), name='new_realty_location'),
    path('new/description/', views.RealtyDescriptionEditView.as_view(), name='new_realty_description'),

    # Images
    path('image/order/', views.RealtyImageOrderView.as_view(), name='image_change_order'),

    # Sitemap
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]
