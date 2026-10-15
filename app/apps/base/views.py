from django.db.models import Avg, Count, Q
from django.shortcuts import render
from django.utils import timezone

from apps.cms.models import FAQ, GalleryImage, Promo, Review, Room, ServiceCategory
from . import seo
from .seo_meta import kymyz_faq
from .models import HeroSlide, SiteSettings


def active_promos():
    today = timezone.localdate()
    return Promo.objects.filter(is_active=True).filter(
        Q(valid_until__isnull=True) | Q(valid_until__gte=today)
    )


def home(request):
    rooms = list(Room.objects.filter(is_active=True).prefetch_related('rates'))
    rating = Review.objects.filter(is_published=True).aggregate(avg=Avg('rating'), count=Count('id'))
    return render(request, 'pages/home.html', {
        'structured_data': [seo.website(request, SiteSettings.load()),
                            seo.lodging_business(request, SiteSettings.load(), rooms, rating)],
        'slides': HeroSlide.objects.filter(is_active=True),
        'rooms': rooms[:3],
        'services': ServiceCategory.objects.filter(show_on_home=True)[:6],
        'promos': active_promos()[:2],
        'reviews': Review.objects.filter(is_published=True)[:8],
        'gallery': GalleryImage.objects.filter(is_active=True)[:8],
    })


def about(request):
    faqs = list(FAQ.objects.all())
    return render(request, 'pages/about.html', {
        'gallery': GalleryImage.objects.filter(is_active=True, category__in=['nature', 'yurts'])[:4],
        'faqs': faqs,
        'structured_data': [seo.faq_page([(f.question, f.answer) for f in faqs])] if faqs else [],
    })


def kymyz(request):
    from apps.cms.views import min_rate
    milk = ServiceCategory.objects.filter(slug='kymyz').prefetch_related('items').first()
    faq = kymyz_faq(min_rate())
    return render(request, 'pages/kymyz.html', {
        'milk': milk,
        'kymyz_faq': faq,
        'structured_data': [seo.faq_page(faq)],
    })


def page_not_found(request, exception):
    return render(request, '404.html', status=404)
