"""Данные для главной страницы админки («Обзор»)."""
from django.urls import reverse
from django.utils import timezone


def dashboard_callback(request, context):
    from apps.cms.models import Review, Room
    from apps.contacts.models import BookingRequest, ContactMessage

    today = timezone.localdate()
    bookings = BookingRequest.objects.select_related('room')
    context.update({
        'kpis': [
            {'title': 'Новые заявки', 'value': bookings.filter(status='new').count(),
             'icon': 'event_available', 'href': reverse('admin:contacts_bookingrequest_changelist') + '?status__exact=new'},
            {'title': 'Ближайшие заезды', 'value': bookings.filter(status='confirmed', check_in__gte=today).count(),
             'icon': 'luggage', 'href': reverse('admin:contacts_bookingrequest_changelist') + '?status__exact=confirmed'},
            {'title': 'Сообщения без ответа', 'value': ContactMessage.objects.filter(is_processed=False).count(),
             'icon': 'mail', 'href': reverse('admin:contacts_contactmessage_changelist') + '?is_processed__exact=0'},
            {'title': 'Отзывы на проверке', 'value': Review.objects.filter(is_published=False).count(),
             'icon': 'reviews', 'href': reverse('admin:cms_review_changelist') + '?is_published__exact=0'},
        ],
        'latest_bookings': [
            {
                'name': b.name,
                'phone': b.phone,
                'dates': f'{b.check_in:%d.%m} — {b.check_out:%d.%m}',
                'room': b.room.name if b.room else '—',
                'status': b.get_status_display(),
                'status_code': b.status,
                'url': reverse('admin:contacts_bookingrequest_change', args=[b.pk]),
            }
            for b in bookings.order_by('-created_at')[:8]
        ],
        'shortcuts': [
            {'title': 'Номера и цены', 'icon': 'bed', 'href': reverse('admin:cms_room_changelist'),
             'text': f'{Room.objects.filter(is_active=True).count()} на сайте'},
            {'title': 'Услуги и прайс', 'icon': 'spa', 'href': reverse('admin:cms_servicecategory_changelist'), 'text': 'массаж, баня, трансфер'},
            {'title': 'Галерея', 'icon': 'photo_library', 'href': reverse('admin:cms_galleryimage_changelist'), 'text': 'фото на сайте'},
            {'title': 'Контакты', 'icon': 'settings', 'href': reverse('admin:base_sitesettings_changelist'), 'text': 'телефон, адрес, сезон'},
        ],
    })
    return context
