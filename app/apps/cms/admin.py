from django.contrib import admin
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display

from .models import FAQ, GalleryImage, PriceItem, Promo, Review, Room, RoomImage, RoomRate, ServiceCategory


class PreviewMixin:
    @admin.display(description='Превью')
    def preview(self, obj):
        return format_html('<img src="{}" style="height:44px;width:64px;object-fit:cover;border-radius:8px">', obj.image_url)


class RoomRateInline(TabularInline):
    model = RoomRate
    extra = 0


class RoomImageInline(TabularInline):
    model = RoomImage
    extra = 0


@admin.register(Room)
class RoomAdmin(PreviewMixin, ModelAdmin):
    list_display = ['preview', 'name', 'kind', 'capacity', 'price_from', 'order', 'is_active']
    list_display_links = ['preview', 'name']
    list_editable = ['order', 'is_active']
    list_filter = ['kind', 'is_active']
    prepopulated_fields = {'slug': ['name']}
    inlines = [RoomRateInline, RoomImageInline]
    fieldsets = [
        ('Основное', {'classes': ['tab'], 'fields': ['name', 'slug', 'kind', 'short_description', 'description',
                                                      'capacity', 'beds', 'amenities', 'order', 'is_active']}),
        ('Главное фото', {'classes': ['tab'], 'fields': ['image', 'static_image']}),
    ]

    @display(description='Цена от, сом/сутки')
    def price_from(self, obj):
        return f'{obj.min_price:,}'.replace(',', ' ') if obj.min_price else '—'


class PriceItemInline(TabularInline):
    model = PriceItem
    extra = 0


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(PreviewMixin, ModelAdmin):
    list_display = ['preview', 'name', 'show_on_home', 'order']
    list_display_links = ['preview', 'name']
    list_editable = ['show_on_home', 'order']
    prepopulated_fields = {'slug': ['name']}
    inlines = [PriceItemInline]
    fieldsets = [
        ('Основное', {'classes': ['tab'], 'fields': ['name', 'slug', 'icon', 'description', 'show_on_home', 'order']}),
        ('Фото', {'classes': ['tab'], 'fields': ['image', 'static_image']}),
    ]


@admin.register(GalleryImage)
class GalleryImageAdmin(PreviewMixin, ModelAdmin):
    list_display = ['preview', 'title', 'category', 'order', 'is_active']
    list_display_links = ['preview', 'title']
    list_editable = ['category', 'order', 'is_active']
    list_filter = ['category', 'is_active']


@admin.register(Review)
class ReviewAdmin(ModelAdmin):
    list_display = ['name', 'city', 'stars', 'short_text', 'source', 'is_published', 'created_at']
    list_editable = ['is_published']
    list_filter = ['is_published', 'rating', 'source']
    search_fields = ['name', 'text']

    @admin.display(description='Отзыв')
    def short_text(self, obj):
        return obj.text[:80]

    @admin.display(description='Оценка', ordering='rating')
    def stars(self, obj):
        return '★' * obj.rating + '☆' * (5 - obj.rating)


@admin.register(Promo)
class PromoAdmin(PreviewMixin, ModelAdmin):
    list_display = ['preview', 'title', 'badge', 'valid_until', 'is_active', 'order']
    list_display_links = ['preview', 'title']
    list_editable = ['is_active', 'order']


@admin.register(FAQ)
class FAQAdmin(ModelAdmin):
    list_display = ['question', 'order']
    list_editable = ['order']
