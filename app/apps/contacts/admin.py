from django.contrib import admin

from .models import BookingRequest, ContactMessage


@admin.register(BookingRequest)
class BookingRequestAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'check_in', 'check_out', 'adults', 'children', 'room',
                    'with_meals', 'status', 'created_at']
    list_filter = ['status', 'room', 'with_meals']
    list_editable = ['status']
    search_fields = ['name', 'phone', 'comment']
    date_hierarchy = 'check_in'
    readonly_fields = ['created_at']


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'short_message', 'is_processed', 'created_at']
    list_filter = ['is_processed']
    list_editable = ['is_processed']
    search_fields = ['name', 'phone', 'message']
    readonly_fields = ['created_at']

    @admin.display(description='Сообщение')
    def short_message(self, obj):
        return obj.message[:80]
