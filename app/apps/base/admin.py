from django.contrib import admin

from .models import HeroSlide, SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'slogan', 'season', 'working_hours']}),
        ('Связь', {'fields': ['phone', 'phone_2', 'whatsapp', 'whatsapp_link', 'instagram', 'email']}),
        ('Адрес и карта', {'fields': ['address', 'address_note', 'map_link', 'map_embed']}),
    ]

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ['title', 'order', 'is_active']
    list_editable = ['order', 'is_active']
