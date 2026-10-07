from django import forms

from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['name', 'city', 'rating', 'text']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Ваше имя'}),
            'city': forms.TextInput(attrs={'placeholder': 'Откуда вы'}),
            'rating': forms.RadioSelect,
            'text': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Расскажите о вашем отдыхе'}),
        }
