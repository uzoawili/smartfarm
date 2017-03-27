from django.db import models


class Station(models.Model):
    """
    model representation of a Smartfarm station which physically comprises
    of a humidity sensor probe and a sprinkler pump outlet, commonly used
    to monitor and control a single plant bed  but can be setup as per the
    users requirements.
    """
    # sensor breakout pins
    SENSOR_PIN_1 = 'GPIO23'
    SENSOR_PIN_2 = 'GPIO24'
    # pump breakout pins
    PUMP_PIN_1 = 'GPIO20'
    PUMP_PIN_2 = 'GPIO21'

    # sensor and probe choices
    SENSORS_PROBES = (
     (SENSOR_PIN_1, 'Sensor Probe 1'),
     (SENSOR_PIN_2, 'Sensor Probe 2'),
    )
    SPRINKLER_PUMPS = (
     (PUMP_PIN_1, 'Sprinkler Pump 1'),
     (PUMP_PIN_2, 'Sprinkler Pump 2'),
    )

    # Sprinkler mode values and choices
    SPRINKLER_MANUAL = "Manual"
    SPRINKLER_AUTO = "Auto"

    SPRINKLER_MODES = (
        (SPRINKLER_AUTO, SPRINKLER_AUTO),
        (SPRINKLER_MANUAL, SPRINKLER_MANUAL),
    )
    # humidity indicator maximum angle
    MAX_HUMIDITY_ANGLE = 300

    # station settings fields
    name = models.CharField(max_length=255, verbose_name='Station Name')
    min_humidity = models.SmallIntegerField(verbose_name='Min Humidity')
    max_humidity = models.SmallIntegerField(verbose_name='Max Humidity')
    sensor = models.CharField(choices=SENSORS_PROBES, max_length=255, verbose_name='Sensor')
    sprinkler = models.CharField(choices=SPRINKLER_PUMPS, max_length=255, verbose_name='Sprinkler')
    enable_notifications = models.BooleanField(default=False, verbose_name='Send Notifications',
                                               help_text='Smartfarm will send email reminders to this email'
                                                         ' if the sprinkler is in manual mode and humidity'
                                                         ' is outside the min - max range.')
    notifications_email = models.EmailField(blank=True, null=True, verbose_name='Notifications Email')

    # station status fields
    is_active = models.BooleanField(blank=True, default=False)
    current_humidity = models.SmallIntegerField(blank=True, null=True, default=None)
    sprinkler_mode = models.CharField(blank=True, choices=SPRINKLER_MODES, default=SPRINKLER_AUTO, max_length=255)
    sprinkler_is_on = models.BooleanField(blank=True, default=False)

    def get_current_humidity_angle(self):
        if self.is_active and self.current_humidity is not None:
            return (self.current_humidity / 100) * self.MAX_HUMIDITY_ANGLE
        return 0

    def getState(self):
        return {
            'is_active': self.is_active,
            'current_humidity': self.current_humidity,
            'sprinkler_mode': self.sprinkler_mode,
            'sprinkler_is_on': self.sprinkler_is_on,
        }
