from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = 'Байтур — кымызолечебница'
admin.site.site_title = 'Байтур'
admin.site.index_title = 'Управление сайтом'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('', include('apps.contacts.urls')),
    path('', include('apps.base.urls')),
    path('', include('apps.cms.urls')),
]

handler404 = 'apps.base.views.page_not_found'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
