from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from apps.base.views import active_promos
from .forms import ReviewForm
from .models import GalleryImage, Review, Room, ServiceCategory


def rooms(request):
    items = Room.objects.filter(is_active=True).prefetch_related('rates')
    return render(request, 'pages/rooms.html', {
        'cottages': [r for r in items if r.kind == Room.KIND_COTTAGE],
        'yurts': [r for r in items if r.kind == Room.KIND_YURT],
    })


def room_detail(request, slug):
    room = get_object_or_404(Room.objects.prefetch_related('rates', 'photos'), slug=slug, is_active=True)
    others = Room.objects.filter(is_active=True).exclude(pk=room.pk).prefetch_related('rates')[:3]
    return render(request, 'pages/room_detail.html', {'room': room, 'others': others})


def services(request):
    return render(request, 'pages/services.html', {
        'categories': ServiceCategory.objects.prefetch_related('items'),
        'promos': active_promos(),
    })


def prices(request):
    return render(request, 'pages/prices.html', {
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
    return render(request, 'pages/reviews.html', {
        'reviews': Review.objects.filter(is_published=True),
        'form': form,
    })
