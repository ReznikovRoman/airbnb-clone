from django.urls import path

from . import views


urlpatterns = [
    path('', views.HomePageView.as_view(), name='home_page'),
    path('robots.txt', views.RobotsView.as_view(), name='robots'),
]
