from django.db import models


class Station(models.Model):
    """
    xxx
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

    # Sprinkler control values
    SPRINKLER_MANUAL = "Manual"
    SPRINKLER_AUTO = "Auto"
    SPRINKLER_ON = 1
    SPRINKLER_OFF = 0

    # Sprinkler control choices
    SPRINKLER_MODES = (
        (SPRINKLER_AUTO, SPRINKLER_AUTO),
        (SPRINKLER_MANUAL, SPRINKLER_MANUAL),
    )
    SPRINKLER_STATUSES = (
        (SPRINKLER_ON, 'ON'),
        (SPRINKLER_OFF, 'OFF'),
    )

    # station settings fields
    name = models.CharField(blank=True, max_length=255, verbose_name='Station Name')
    min_humidity = models.SmallIntegerField(verbose_name='Min Humidity')
    max_humidity = models.SmallIntegerField(verbose_name='Max Humidity')
    sensor = models.CharField(choices=SENSORS_PROBES, max_length=255, verbose_name='Sensor')
    sprinkler = models.CharField(choices=SPRINKLER_PUMPS, max_length=255, verbose_name='Sprinkler')
    enable_notifications = models.BooleanField(default=False, verbose_name='Send Notifications')
    notifications_email = models.EmailField(blank=True, null=True, verbose_name='Notifications Email')

    # station status fields
    is_active = models.BooleanField(default=False)
    current_humidity = models.SmallIntegerField(blank=True, null=True)
    sprinkler_mode = models.CharField(choices=SPRINKLER_MODES, default=SPRINKLER_AUTO, max_length=255)
    sprinkler_status = models.CharField(choices=SPRINKLER_STATUSES, default=SPRINKLER_OFF, max_length=255)