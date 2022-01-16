from django.http import HttpResponse
from django.urls import path

from . import views


urlpatterns = [
    path('', views.HomePageView.as_view(), name='home_page'),
    path('healthcheck/', lambda response: HttpResponse(), name='healthcheck'),
    path('robots.txt', views.RobotsView.as_view(), name='robots'),
]
