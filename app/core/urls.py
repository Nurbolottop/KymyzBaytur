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


def llms_txt(request):
    """Справка о нас для ИИ-ассистентов (стандарт llms.txt) — собирается из актуальных данных."""
    from apps.base.models import SiteSettings
    from apps.base.seo_meta import kymyz_faq
    from apps.cms.models import FAQ, ServiceCategory
    from apps.cms.views import min_rate

    min_price = min_rate()
    response = render(request, 'llms.txt', {
        'base': f'{request.scheme}://{request.get_host()}',
        'site': SiteSettings.load(),
        'min_price': min_price,
        'rooms': Room.objects.filter(is_active=True).prefetch_related('rates'),
        'categories': ServiceCategory.objects.prefetch_related('items'),
        'faqs': FAQ.objects.all(),
        'kymyz_faq': kymyz_faq(min_price),
    }, content_type='text/markdown; charset=utf-8')
    # обычные пробелы в числах вместо неразрывных — так текст проще читать ИИ
    response.content = response.content.decode().replace('\xa0', ' ').encode()
    return response


def sitemap(request):
    from apps.base.models import HeroSlide
    from apps.cms.models import GalleryImage, ServiceCategory

    def img(url, title):
        return {'loc': request.build_absolute_uri(url), 'title': title}

    pages = [('home', '1.0'), ('kymyz', '0.9'), ('rooms', '0.9'), ('prices', '0.9'), ('booking', '0.8'),
             ('services', '0.8'), ('about', '0.7'), ('gallery', '0.7'), ('reviews', '0.6'), ('contacts', '0.7')]
    images = {
        'home': [img(s.image_url, s.title) for s in HeroSlide.objects.filter(is_active=True)],
        'gallery': [img(g.image_url, g.title or 'Кумысолечебница «Байтур», Суусамыр')
                    for g in GalleryImage.objects.filter(is_active=True)],
        'services': [img(c.image_url, c.name) for c in ServiceCategory.objects.all()],
    }
    entries = [{'path': reverse(name), 'priority': priority, 'images': images.get(name, [])}
               for name, priority in pages]
    for room in Room.objects.filter(is_active=True).prefetch_related('photos'):
        room_images = [img(room.image_url, room.name)] + [img(p.image_url, room.name) for p in room.photos.all()]
        entries.append({'path': room.get_absolute_url(), 'priority': '0.8', 'images': room_images})
    return render(request, 'sitemap.xml', {'entries': entries, 'lastmod': CONTENT_DATE.isoformat()},
                  content_type='application/xml')


INDEXNOW_KEY = '5b8f3c2a9e7d41f6a0c4b7e2d9f1a863'


def indexnow_key(request):
    """Ключ IndexNow: подтверждает, что уведомления об изменениях шлёт владелец сайта."""
    return HttpResponse(INDEXNOW_KEY, content_type='text/plain')


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
    path('llms.txt', llms_txt),
    path(f'{INDEXNOW_KEY}.txt', indexnow_key),
    path('llms-full.txt', llms_txt),
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('', include('apps.contacts.urls')),
    path('', include('apps.base.urls')),
    path('', include('apps.cms.urls')),
]

handler404 = 'apps.base.views.page_not_found'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
