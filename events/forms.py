from django import forms
from .models import Event
from django.utils import timezone


class EventForm(forms.ModelForm):
    cover_image = forms.ImageField(required=False)
    class Meta:
        model = Event
        fields = [
            'event_name',
            'about',
            'cover_image',
            'place',
            'event_date',
            'last_registration_date',
            'fees',
            'contact_number',
            'registration_link',
        ]
        widgets = {
            'about': forms.Textarea(attrs={'rows': 4}),
            'event_date': forms.DateInput(attrs={'type': 'date'}),
            'last_registration_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_event_date(self):
        date = self.cleaned_data.get('event_date')
        if date and date < timezone.now().date():
            raise forms.ValidationError('Event date cannot be in the past.')
        return date

    def clean_last_registration_date(self):
        reg_date = self.cleaned_data.get('last_registration_date')
        event_date = self.cleaned_data.get('event_date')
        if reg_date and reg_date < timezone.now().date():
            raise forms.ValidationError('Last registration date cannot be in the past.')
        if reg_date and event_date and reg_date > event_date:
            raise forms.ValidationError('Last registration date cannot be after event date.')
        return reg_date

    def clean_fees(self):
        fees = self.cleaned_data.get('fees')
        if fees is None or fees < 0:
            raise forms.ValidationError('Fees cannot be negative.')
        return fees


class RepresentativeRequestForm(forms.Form):
    reason = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        label='Why do you want to become a College Representative?',
        help_text='Briefly explain your role in your college.'
    )