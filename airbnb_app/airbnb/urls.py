import debug_toolbar
from rest_framework_simplejwt.views import TokenRefreshView

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.flatpages import views as flatpage_views
from django.urls import include, path

from accounts.api.views import CustomTokenObtainPairView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('pages/', include('django.contrib.flatpages.urls')),

    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('api-auth/', include('rest_framework.urls')),

    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('realty/', include('realty.urls', namespace='realty')),
    path('hosts/', include('hosts.urls', namespace='hosts')),
    path('subscribers/', include('subscribers.urls', namespace='subscribers')),

    path('api/v1/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/', include('realty.api.urls', namespace='api')),

    path('', include('main.urls')),
]

urlpatterns += [
    path('about/', flatpage_views.flatpage, {'url': 'about/'}, name='about'),
    path('contacts/', flatpage_views.flatpage, {'url': 'contacts/'}, name='contacts'),
]

handler400 = 'main.views.bad_request_view'
handler403 = 'main.views.permission_denied_view'
handler404 = 'main.views.page_not_found_view'
handler500 = 'main.views.server_error_view'


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
