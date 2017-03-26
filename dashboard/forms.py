from django import forms
from .models import Station


class StationSettingsForm(forms.ModelForm):
    """
    Form that creates and updating a station's settings
    """
    min_humidity = forms.IntegerField(min_value=0, max_value=100)
    max_humidity = forms.IntegerField(min_value=0, max_value=100)

    class Meta:
        model = Station
        fields = ('name', 'min_humidity', 'max_humidity',
                  'sensor', 'sprinkler', 'enable_notifications',
                  'notifications_email')

class StationStateForm(forms.ModelForm):
    """
    Form that creates and updating a stations state fields
    """
    class Meta:
        model = Station
        fields = ('is_active', 'current_humidity',
                  'sprinkler_mode', 'sprinkler_status')