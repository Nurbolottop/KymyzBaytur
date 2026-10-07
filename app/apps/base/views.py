from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone

from apps.cms.models import FAQ, GalleryImage, Promo, Review, Room, ServiceCategory
from .models import HeroSlide


def active_promos():
    today = timezone.localdate()
    return Promo.objects.filter(is_active=True).filter(
        Q(valid_until__isnull=True) | Q(valid_until__gte=today)
    )


def home(request):
    return render(request, 'pages/home.html', {
        'slides': HeroSlide.objects.filter(is_active=True),
        'rooms': Room.objects.filter(is_active=True).prefetch_related('rates')[:3],
        'services': ServiceCategory.objects.filter(show_on_home=True)[:6],
        'promos': active_promos()[:2],
        'reviews': Review.objects.filter(is_published=True)[:8],
        'gallery': GalleryImage.objects.filter(is_active=True)[:8],
    })


def about(request):
    return render(request, 'pages/about.html', {
        'gallery': GalleryImage.objects.filter(is_active=True, category__in=['nature', 'yurts'])[:4],
        'faqs': FAQ.objects.all(),
    })


def kymyz(request):
    milk = ServiceCategory.objects.filter(slug='kymyz').prefetch_related('items').first()
    return render(request, 'pages/kymyz.html', {'milk': milk})


def page_not_found(request, exception):
    return render(request, '404.html', status=404)
