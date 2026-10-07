from django.urls import path

from . import views

urlpatterns = [
    path('rooms/', views.rooms, name='rooms'),
    path('rooms/<slug:slug>/', views.room_detail, name='room_detail'),
    path('services/', views.services, name='services'),
    path('prices/', views.prices, name='prices'),
    path('gallery/', views.gallery, name='gallery'),
    path('reviews/', views.reviews, name='reviews'),
]
