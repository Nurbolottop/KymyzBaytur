from .models import SiteSettings
from .seo_meta import page_meta


def site_settings(request):
    site = SiteSettings.load()
    match = getattr(request, 'resolver_match', None)
    url_name = match.url_name if match else None
    min_price = None
    if url_name in ('rooms', 'prices'):
        from apps.cms.views import min_rate
        min_price = min_rate()
    return {'site': site, 'meta': page_meta(url_name, site, min_price)}
