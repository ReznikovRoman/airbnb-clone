import debug_toolbar

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.contrib.flatpages import views as flatpage_views
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('pages/', include('django.contrib.flatpages.urls')),

    path('accounts/', include('allauth.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),

    path('realty/', include('realty.urls', namespace='realty')),
    path('hosts/', include('hosts.urls', namespace='hosts')),
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
