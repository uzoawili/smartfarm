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
                  'sensor', 'sprinkler', 'blinker', 'latitude', 'longitude',
                  'enable_notifications', 'notifications_email')

class StationStateForm(forms.ModelForm):
    """
    Form that creates and updating a stations state fields
    """
    class Meta:
        model = Station
        fields = ('is_active', 'current_humidity',
                  'sprinkler_mode', 'sprinkler_is_on')

    def save(self, commit=True):
        instance = super(StationStateForm, self).save(commit=False)
        if not instance.is_active:
            instance.sprinkler_is_on = False
        instance.save()
        return instance