from django import forms
from .models import TicketAlert

class TicketAlertForm(forms.ModelForm):
    class Meta:
        model = TicketAlert
        fields = ['user_email', 'movie_name', 'bms_url', 'theatre_filter','target_date']
        widgets = {
            'user_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com'}),
            'movie_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Avengers: Secret Wars'}),
            'bms_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://in.bookmyshow.com/buytickets/...'}),
            'theatre_filter': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional (e.g. PVR, Srinivasa)'}),
            'target_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }