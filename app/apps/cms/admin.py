from django.contrib import admin
from django.utils.html import format_html

from .models import FAQ, GalleryImage, PriceItem, Promo, Review, Room, RoomImage, RoomRate, ServiceCategory


class PreviewMixin:
    @admin.display(description='Превью')
    def preview(self, obj):
        return format_html('<img src="{}" style="height:48px;border-radius:6px">', obj.image_url)


class RoomRateInline(admin.TabularInline):
    model = RoomRate
    extra = 0


class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 0


@admin.register(Room)
class RoomAdmin(PreviewMixin, admin.ModelAdmin):
    list_display = ['preview', 'name', 'kind', 'capacity', 'min_price', 'order', 'is_active']
    list_display_links = ['preview', 'name']
    list_editable = ['order', 'is_active']
    list_filter = ['kind', 'is_active']
    prepopulated_fields = {'slug': ['name']}
    inlines = [RoomRateInline, RoomImageInline]


class PriceItemInline(admin.TabularInline):
    model = PriceItem
    extra = 0


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(PreviewMixin, admin.ModelAdmin):
    list_display = ['preview', 'name', 'show_on_home', 'order']
    list_display_links = ['preview', 'name']
    list_editable = ['show_on_home', 'order']
    prepopulated_fields = {'slug': ['name']}
    inlines = [PriceItemInline]


@admin.register(GalleryImage)
class GalleryImageAdmin(PreviewMixin, admin.ModelAdmin):
    list_display = ['preview', 'title', 'category', 'order', 'is_active']
    list_display_links = ['preview', 'title']
    list_editable = ['category', 'order', 'is_active']
    list_filter = ['category', 'is_active']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'rating', 'short_text', 'source', 'is_published', 'created_at']
    list_editable = ['is_published']
    list_filter = ['is_published', 'rating', 'source']
    search_fields = ['name', 'text']

    @admin.display(description='Отзыв')
    def short_text(self, obj):
        return obj.text[:80]


@admin.register(Promo)
class PromoAdmin(PreviewMixin, admin.ModelAdmin):
    list_display = ['preview', 'title', 'badge', 'valid_until', 'is_active', 'order']
    list_display_links = ['preview', 'title']
    list_editable = ['is_active', 'order']


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'order']
    list_editable = ['order']
