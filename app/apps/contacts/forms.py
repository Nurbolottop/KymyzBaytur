from django import forms
from django.utils import timezone

from apps.cms.models import Room
from .models import BookingRequest, ContactMessage


class BookingForm(forms.ModelForm):
    class Meta:
        model = BookingRequest
        fields = ['name', 'phone', 'check_in', 'check_out', 'adults', 'children',
                  'room', 'with_meals', 'comment']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Как к вам обращаться', 'autocomplete': 'name'}),
            'phone': forms.TextInput(attrs={'placeholder': '+996 ___ ___ ___', 'autocomplete': 'tel',
                                            'inputmode': 'tel'}),
            'check_in': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'check_out': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'adults': forms.NumberInput(attrs={'min': 1, 'max': 20}),
            'children': forms.NumberInput(attrs={'min': 0, 'max': 20}),
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Трансфер, пожелания, курс кымызолечения…'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['room'].queryset = Room.objects.filter(is_active=True)
        self.fields['room'].empty_label = 'Подобрать на месте'
        self.fields['adults'].min_value = 1

    def clean(self):
        data = super().clean()
        check_in, check_out = data.get('check_in'), data.get('check_out')
        if check_in and check_in < timezone.localdate():
            self.add_error('check_in', 'Дата заезда уже прошла.')
        if check_in and check_out and check_out <= check_in:
            self.add_error('check_out', 'Дата выезда должна быть позже даты заезда.')
        return data


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'phone', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Ваше имя', 'autocomplete': 'name'}),
            'phone': forms.TextInput(attrs={'placeholder': '+996 ___ ___ ___', 'autocomplete': 'tel',
                                            'inputmode': 'tel'}),
            'message': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Ваш вопрос'}),
        }
