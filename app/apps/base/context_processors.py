from django.urls import reverse

from .models import SiteSettings
from .seo_meta import page_meta

# Короткие названия страниц для хлебных крошек в разметке
CRUMBS = {
    'about': 'О нас', 'kymyz': 'Кымызолечение', 'rooms': 'Номера и юрты', 'services': 'Услуги',
    'prices': 'Цены', 'gallery': 'Галерея', 'reviews': 'Отзывы', 'contacts': 'Контакты',
    'booking': 'Бронирование',
}


def site_settings(request):
    from . import seo

    site = SiteSettings.load()
    match = getattr(request, 'resolver_match', None)
    url_name = match.url_name if match else None
    min_price = None
    if url_name in ('rooms', 'prices', 'kymyz'):
        from apps.cms.views import min_rate
        min_price = min_rate()
    meta = page_meta(url_name, site, min_price)

    # Разметка страницы: что это за страница и где она в структуре сайта
    page_ld = []
    if url_name in CRUMBS:
        page_type = {'about': 'AboutPage', 'contacts': 'ContactPage', 'gallery': 'CollectionPage',
                     }.get(url_name, 'WebPage')
        page_ld = [
            seo.webpage(request, meta['title'], meta['description'], page_type),
            seo.breadcrumbs(request, [('Главная', '/'), (CRUMBS[url_name], reverse(url_name))]),
        ]
    return {'site': site, 'meta': meta, 'page_ld': page_ld}
