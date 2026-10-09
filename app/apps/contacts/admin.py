from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.decorators import display

from .models import BookingRequest, ContactMessage


@admin.register(BookingRequest)
class BookingRequestAdmin(ModelAdmin):
    list_display = ['name', 'phone', 'dates', 'guests', 'room', 'with_meals', 'status_badge', 'created_at']
    list_display_links = ['name']
    list_filter = ['status', 'room', 'with_meals']
    search_fields = ['name', 'phone', 'comment']
    date_hierarchy = 'check_in'
    readonly_fields = ['created_at']

    @display(description='Даты', ordering='check_in')
    def dates(self, obj):
        return f'{obj.check_in:%d.%m} — {obj.check_out:%d.%m.%Y} ({obj.nights} ноч.)'

    @display(description='Гости')
    def guests(self, obj):
        return f'{obj.adults} взр.' + (f' + {obj.children} дет.' if obj.children else '')

    @display(description='Статус', ordering='status', label={'Новая': 'warning', 'Подтверждена': 'success', 'Отменена': 'danger'})
    def status_badge(self, obj):
        return obj.get_status_display()


@admin.register(ContactMessage)
class ContactMessageAdmin(ModelAdmin):
    list_display = ['name', 'phone', 'short_message', 'is_processed', 'created_at']
    list_filter = ['is_processed']
    list_editable = ['is_processed']
    search_fields = ['name', 'phone', 'message']
    readonly_fields = ['created_at']

    @admin.display(description='Сообщение')
    def short_message(self, obj):
        return obj.message[:80]
