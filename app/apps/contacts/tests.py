import datetime

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.cms.models import Review, Room
from apps.contacts.models import BookingRequest, ContactMessage


class BookingTest(TestCase):
    def booking_data(self, **overrides):
        start = timezone.localdate() + datetime.timedelta(days=10)
        data = {
            'name': 'Тест', 'phone': '+996 700 000 000',
            'check_in': start, 'check_out': start + datetime.timedelta(days=5),
            'adults': 2, 'children': 0, 'room': Room.objects.get(slug='lux').pk,
            'with_meals': 'on', 'comment': '',
        }
        data.update(overrides)
        return data

    def test_booking_created(self):
        response = self.client.post(reverse('booking'), self.booking_data())
        self.assertRedirects(response, reverse('booking_success'))
        booking = BookingRequest.objects.get()
        self.assertEqual(booking.nights, 5)
        self.assertTrue(booking.with_meals)

    def test_checkout_before_checkin_rejected(self):
        data = self.booking_data()
        data['check_out'] = data['check_in']
        response = self.client.post(reverse('booking'), data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(BookingRequest.objects.exists())

    def test_past_checkin_rejected(self):
        past = timezone.localdate() - datetime.timedelta(days=3)
        response = self.client.post(reverse('booking'), self.booking_data(check_in=past))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(BookingRequest.objects.exists())

    def test_room_prefilled_from_query(self):
        response = self.client.get(reverse('booking') + '?room=lux')
        self.assertEqual(response.context['form'].initial['room'].slug, 'lux')


class ContactAndReviewTest(TestCase):
    def test_contact_message(self):
        response = self.client.post(reverse('contacts'),
                                    {'name': 'Тест', 'phone': '0700', 'message': 'Есть места?'})
        self.assertRedirects(response, reverse('contacts'))
        self.assertTrue(ContactMessage.objects.exists())

    def test_review_needs_moderation(self):
        self.client.post(reverse('reviews'), {'name': 'Аноним', 'city': '', 'rating': 5, 'text': 'Супер'})
        review = Review.objects.get(name='Аноним')
        self.assertFalse(review.is_published)
        self.assertNotContains(self.client.get(reverse('reviews')), 'Супер')
