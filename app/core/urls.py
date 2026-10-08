from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView

from apps.cms.models import Room


def sitemap(request):
    names = ['home', 'about', 'kymyz', 'rooms', 'services', 'prices', 'gallery', 'reviews', 'contacts', 'booking']
    paths = [reverse(n) for n in names] + [r.get_absolute_url() for r in Room.objects.filter(is_active=True)]
    return render(request, 'sitemap.xml', {'paths': paths}, content_type='application/xml')

admin.site.site_header = 'Байтур — кымызолечебница'
admin.site.site_title = 'Байтур'
admin.site.index_title = 'Управление сайтом'

urlpatterns = [
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    path('sitemap.xml', sitemap),
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('', include('apps.contacts.urls')),
    path('', include('apps.base.urls')),
    path('', include('apps.cms.urls')),
]

handler404 = 'apps.base.views.page_not_found'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
