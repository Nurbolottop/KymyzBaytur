from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView

from apps.cms.models import Room


def _content_date():
    """Дата последнего изменения контента сайта: шаблоны и статика проекта."""
    import datetime
    from pathlib import Path
    latest = max(
        f.stat().st_mtime
        for folder in (settings.BASE_DIR / 'templates', settings.BASE_DIR / 'static' / 'css')
        for f in Path(folder).rglob('*') if f.is_file()
    )
    return datetime.date.fromtimestamp(latest)


CONTENT_DATE = _content_date()


def sitemap(request):
    pages = [('home', '1.0'), ('kymyz', '0.9'), ('rooms', '0.9'), ('prices', '0.9'), ('booking', '0.8'),
             ('services', '0.8'), ('about', '0.7'), ('gallery', '0.7'), ('reviews', '0.6'), ('contacts', '0.7')]
    entries = [(reverse(name), priority) for name, priority in pages]
    entries += [(room.get_absolute_url(), '0.8') for room in Room.objects.filter(is_active=True)]
    return render(request, 'sitemap.xml', {'entries': entries, 'lastmod': CONTENT_DATE.isoformat()},
                  content_type='application/xml')


admin.site.site_header = 'Байтур — кымызолечебница'
admin.site.site_title = 'Байтур'
admin.site.index_title = 'Управление сайтом'

urlpatterns = [
    # Подтверждение прав в Google Search Console — файл не удалять
    path('google7cea8f04d4a415ac.html',
         lambda request: HttpResponse('google-site-verification: google7cea8f04d4a415ac.html', content_type='text/html')),
    # Подтверждение прав в Яндекс Вебмастере — файл не удалять
    path('yandex_eb9939a8c3ea03f0.html',
         lambda request: HttpResponse(
             '<html>\n    <head>\n        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">\n'
             '    </head>\n    <body>Verification: eb9939a8c3ea03f0</body>\n</html>\n',
             content_type='text/html; charset=UTF-8')),
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
