import debug_toolbar

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.contrib.flatpages import views as flatpage_views
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('pages/', include('django.contrib.flatpages.urls')),

    path('', include('main.urls')),
]

urlpatterns += [
    path('about/', flatpage_views.flatpage, {'url': 'about/'}, name='about'),
    path('contacts/', flatpage_views.flatpage, {'url': 'contacts/'}, name='contacts'),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )

    urlpatterns += [
        path('__debug__/', include(debug_toolbar.urls)),
    ]
