from django.contrib import messages
from django.shortcuts import redirect, render

from apps.cms.models import Room
from .forms import BookingForm, ContactForm
from .notify import send_telegram


def booking(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            obj = form.save()
            send_telegram(
                '🛎 Новая заявка на бронь\n'
                f'Имя: {obj.name}\nТелефон: {obj.phone}\n'
                f'Даты: {obj.check_in:%d.%m.%Y} — {obj.check_out:%d.%m.%Y} ({obj.nights} ноч.)\n'
                f'Гости: {obj.adults} взр. + {obj.children} дет.\n'
                f'Номер: {obj.room or "не выбран"}\n'
                f'Питание и кымыз: {"да" if obj.with_meals else "нет"}\n'
                f'Комментарий: {obj.comment or "—"}'
            )
            return redirect('booking_success')
    else:
        initial = {}
        for key in ('check_in', 'check_out', 'adults', 'children'):
            if request.GET.get(key):
                initial[key] = request.GET[key]
        room_slug = request.GET.get('room')
        if room_slug:
            initial['room'] = Room.objects.filter(slug=room_slug, is_active=True).first()
        form = BookingForm(initial=initial)

    rooms = Room.objects.filter(is_active=True).prefetch_related('rates')
    room_rates = {
        room.pk: {
            'name': room.name,
            'rates': [{'guests': r.guests, 'full': r.price_full, 'room': r.price_room_only}
                      for r in room.rates.all()],
        }
        for room in rooms
    }
    return render(request, 'pages/booking.html', {'form': form, 'room_rates': room_rates})


def booking_success(request):
    return render(request, 'pages/booking_success.html')


def contacts(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            obj = form.save()
            send_telegram(f'✉️ Сообщение с сайта\nИмя: {obj.name}\nТелефон: {obj.phone}\n\n{obj.message}')
            messages.success(request, 'Спасибо! Мы перезвоним вам в ближайшее время.')
            return redirect('contacts')
    else:
        form = ContactForm()
    return render(request, 'pages/contacts.html', {'form': form})
