from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    url(r'', include('eshop.urls', namespace='eshop')),
    # url(r'^payments/', include('djstripe.urls', namespace="djstripe")),
    url('home/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)