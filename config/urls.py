from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import include, path


urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/v1/auth/', include("api.v1.auth.urls")),
    path('api/v1/drive/', include("api.v1.drive.urls")),
]

if settings.DEBUG:
    urlpatterns += (
        static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) +
        static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    )