from django.urls import path

from . import views

urlpatterns = [
    path('contacts/', views.contacts, name='contacts'),
    path('booking/', views.booking, name='booking'),
    path('booking/success/', views.booking_success, name='booking_success'),
]
