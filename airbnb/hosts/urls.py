from django.urls import path

from realty.views import RealtyEditView


app_name = 'hosts'

urlpatterns = [
    path('become-a-host/', RealtyEditView.as_view(), name='become_a_host'),
]
