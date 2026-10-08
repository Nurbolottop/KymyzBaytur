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
