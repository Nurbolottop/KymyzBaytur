from django.contrib import messages
from django.db.models import Avg, Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from apps.base import seo
from apps.base.models import SiteSettings
from apps.base.views import active_promos
from .forms import ReviewForm
from .models import GalleryImage, Review, Room, RoomRate, ServiceCategory


def min_rate():
    """Самая низкая цена за сутки с питанием и кымызом — для описаний в поиске."""
    rate = RoomRate.objects.filter(room__is_active=True).order_by('price_full').first()
    return rate.price_full if rate else None


def rooms(request):
    items = Room.objects.filter(is_active=True).prefetch_related('rates')
    return render(request, 'pages/rooms.html', {
        'min_price': min_rate(),
        'cottages': [r for r in items if r.kind == Room.KIND_COTTAGE],
        'yurts': [r for r in items if r.kind == Room.KIND_YURT],
    })


def room_detail(request, slug):
    room = get_object_or_404(Room.objects.prefetch_related('rates', 'photos'), slug=slug, is_active=True)
    others = Room.objects.filter(is_active=True).exclude(pk=room.pk).prefetch_related('rates')[:3]
    return render(request, 'pages/room_detail.html', {
        'room': room,
        'others': others,
        'structured_data': [
            seo.room_page(request, SiteSettings.load(), room),
            seo.breadcrumbs(request, [('Главная', '/'), ('Номера', reverse('rooms')), (room.name, room.get_absolute_url())]),
        ],
    })


def services(request):
    return render(request, 'pages/services.html', {
        'categories': ServiceCategory.objects.prefetch_related('items'),
        'promos': active_promos(),
    })


def prices(request):
    return render(request, 'pages/prices.html', {
        'min_price': min_rate(),
        'rooms': Room.objects.filter(is_active=True).prefetch_related('rates'),
        'categories': ServiceCategory.objects.prefetch_related('items'),
    })


def gallery(request):
    return render(request, 'pages/gallery.html', {
        'images': GalleryImage.objects.filter(is_active=True),
        'categories': GalleryImage.CATEGORY_CHOICES,
    })


def reviews(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Спасибо за отзыв! Он появится на сайте после проверки.')
            return redirect('reviews')
    else:
        form = ReviewForm()
    published = Review.objects.filter(is_published=True)
    rating = published.aggregate(avg=Avg('rating'), count=Count('id'))
    return render(request, 'pages/reviews.html', {
        'reviews': published,
        'form': form,
        'rating': rating,
        'structured_data': [seo.reviews_page(request, SiteSettings.load(), published, rating)],
    })
