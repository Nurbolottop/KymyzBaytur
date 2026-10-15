from django.test import TestCase
from django.urls import reverse

from apps.cms.models import Room


class PagesTest(TestCase):
    def test_pages_render(self):
        names = ['home', 'about', 'kymyz', 'rooms', 'services', 'prices', 'gallery',
                 'reviews', 'contacts', 'booking', 'booking_success']
        for name in names:
            with self.subTest(page=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, 200)

    def test_seeded_content_is_shown(self):
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'Суусамыр')
        self.assertContains(response, '+996 770 797 370')

    def test_room_detail(self):
        room = Room.objects.get(slug='lux')
        response = self.client.get(room.get_absolute_url())
        self.assertContains(response, 'Люкс')
        self.assertContains(response, '12')  # 12 880 сом

    def test_unknown_room_404(self):
        self.assertEqual(self.client.get('/rooms/nope/').status_code, 404)


class SeoFilesTest(TestCase):
    def test_robots_and_sitemap(self):
        robots = self.client.get('/robots.txt')
        self.assertEqual(robots['Content-Type'], 'text/plain')
        self.assertContains(robots, 'Sitemap:')
        self.assertContains(self.client.get('/sitemap.xml'), '/rooms/lux/')

    def test_google_verification(self):
        self.assertContains(self.client.get('/google7cea8f04d4a415ac.html'),
                            'google-site-verification: google7cea8f04d4a415ac.html')

    def test_seo_tags(self):
        import json, re
        home = self.client.get('/?utm_source=x').content.decode()
        self.assertIn('<link rel="canonical" href="http://testserver/">', home)
        blocks = [json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', home)]
        data = next(b for b in blocks if b['@type'] == 'LodgingBusiness')
        self.assertIn('geo', data)
        self.assertIn('<lastmod>', self.client.get('/sitemap.xml').content.decode())
        descriptions = {re.search(r'<meta name="description" content="([^"]*)"', self.client.get(u).content.decode()).group(1)
                        for u in ['/', '/about/', '/prices/', '/rooms/', '/contacts/', '/gallery/', '/reviews/', '/services/', '/booking/']}
        self.assertEqual(len(descriptions), 9)
        gallery = self.client.get('/gallery/').content.decode()
        empty_alts = [tag for tag in re.findall(r'<img[^>]*>', gallery) if 'alt=""' in tag and 'brand__logo' not in tag]
        self.assertEqual(empty_alts, [])

    def test_yandex_verification(self):
        self.assertContains(self.client.get('/yandex_eb9939a8c3ea03f0.html'), 'Verification: eb9939a8c3ea03f0')


class AdminThemeTest(TestCase):
    def test_login_page(self):
        response = self.client.get('/admin/login/')
        self.assertContains(response, 'Панель управления')
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_wrong_password_shows_error(self):
        response = self.client.post('/admin/login/', {'username': 'x', 'password': 'y'})
        self.assertContains(response, 'class="alert"')


class SeoMetaTest(TestCase):
    def test_titles_unique_and_contain_keywords(self):
        import re
        urls = ['/', '/about/', '/kymyz/', '/rooms/', '/rooms/lux/', '/services/', '/prices/',
                '/gallery/', '/reviews/', '/contacts/', '/booking/']
        titles, descriptions = set(), set()
        for url in urls:
            html = self.client.get(url).content.decode()
            title = re.search(r'<title>(.*?)</title>', html, re.S).group(1).strip()
            og = re.search(r'<meta property="og:title" content="([^"]*)"', html).group(1)
            desc = re.search(r'<meta name="description" content="([^"]*)"', html).group(1)
            self.assertEqual(title.replace('&quot;', '"'), og.replace('&quot;', '"'), url)
            self.assertLessEqual(len(desc), 200, url)
            self.assertIn('meta name="keywords"', html)
            titles.add(title)
            descriptions.add(desc)
        self.assertEqual(len(titles), len(urls))
        self.assertEqual(len(descriptions), len(urls))
        self.assertIn('Кумысолечение', self.client.get('/').content.decode())
        self.assertIn('от 6 980 сом', self.client.get('/prices/').content.decode())


class AiReadinessTest(TestCase):
    def test_llms_txt(self):
        r = self.client.get('/llms.txt')
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r['Content-Type'].startswith('text/markdown'))
        text = r.content.decode()
        for needle in ['кумысолечение', 'Суусамыр', '+996 770 797 370', 'Люкс', '12 880', 'Массаж', 'Где пройти кумысолечение']:
            self.assertIn(needle, text)

    def test_robots_allows_ai_bots(self):
        text = self.client.get('/robots.txt').content.decode()
        for bot in ['GPTBot', 'OAI-SearchBot', 'PerplexityBot', 'ClaudeBot', 'Google-Extended']:
            self.assertIn(f'User-agent: {bot}', text)

    def test_structured_data(self):
        import json, re
        def ld(url):
            html = self.client.get(url).content.decode()
            return [json.loads(x) for x in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html)]
        types = lambda url: {d['@type'] for d in ld(url)}
        self.assertTrue({'WebSite', 'LodgingBusiness'} <= types('/'))
        self.assertIn('FAQPage', types('/kymyz/'))
        self.assertIn('FAQPage', types('/about/'))
        self.assertIn('BreadcrumbList', types('/prices/'))
        catalog = [d for d in ld('/services/') if 'hasOfferCatalog' in d][0]
        self.assertTrue(catalog['hasOfferCatalog']['itemListElement'])

    def test_sitemap_images_and_indexnow(self):
        xml = self.client.get('/sitemap.xml').content.decode()
        self.assertIn('<image:image>', xml)
        from core.urls import INDEXNOW_KEY
        self.assertContains(self.client.get(f'/{INDEXNOW_KEY}.txt'), INDEXNOW_KEY)
