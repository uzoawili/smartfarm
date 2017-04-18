import requests
import json
import random
import time
from datetime import datetime, timedelta

from django.db import models
from django.conf import settings

from jsonfield import JSONField

import RPi.GPIO as GPIO

# import SPI (for hardware SPI) and MCP3008 library
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import spidev



# for pin numbering, choose BCM(aka GPIO numbering)
GPIO.setmode(GPIO.BCM)


class Station(models.Model):
    """
    model representing a Smartfarm station which physically comprises
    of a humidity sensor probe and a sprinkler pump outlet, commonly used
    to monitor and control a single plant bed  but can be setup as per the
    users requirements.
    """
    # sensor breakout pins
    SENSOR_PIN_1 = '17'
    SPI_PORT = 0
    SPI_DEVICE = 0
    SENSOR_ADC_CHANNEL = 0
   
    # pump breakout pins
    PUMP_PIN_1 = '23'
    
    # Blinker pin:
    BLINKER_PIN_1 = '24'

    # sensor, probe and blinker choices
    SENSORS_PROBES = (
     (SENSOR_PIN_1, 'Sensor Probe 1'),
    )
    SPRINKLER_PUMPS = (
     (PUMP_PIN_1, 'Sprinkler Pump 1'),
    )
    BLINKER_PINS = (
        (BLINKER_PIN_1, 'Blinker Pin 1'),
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
    longitude = models.FloatField(blank=True, null=True, verbose_name='Longitude')
    latitude = models.FloatField(blank=True, null=True, verbose_name='latitude')
    sensor = models.CharField(choices=SENSORS_PROBES, max_length=255, verbose_name='Sensor')
    sprinkler = models.CharField(choices=SPRINKLER_PUMPS, max_length=255, verbose_name='Sprinkler')
    blinker = models.CharField(choices=BLINKER_PINS, max_length=255, verbose_name='Blinker')
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

    def get_state(self):
        station_state = {
            'is_active': self.is_active,
            'current_humidity': self.current_humidity,
            'sprinkler_mode': self.sprinkler_mode,
            'sprinkler_is_on': self.sprinkler_is_on,
        }
        return station_state

    def sync_with_io(self):
        if self.is_active:
            self.setup_io()
            self.trigger_sprinkler()
            self.read_sensor()
            self.blink()

    def setup_io(self):
        self.mcp = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(self.SPI_PORT, self.SPI_DEVICE))
        # if not GPIO.gpio_function(int(self.sprinkler)) == GPIO.OUT:
        GPIO.setup(int(self.sprinkler), GPIO.OUT)
        # if not GPIO.gpio_function(int(self.blinker)) == GPIO.OUT:
        GPIO.setup(int(self.blinker), GPIO.OUT)

    def trigger_sprinkler(self):
        GPIO.output(int(self.sprinkler), self.sprinkler_is_on)

    def read_sensor(self):
        # import pdb; pdb.set_trace()
        sensor_value = self.mcp.read_adc(self.SENSOR_ADC_CHANNEL)
        self.current_humidity = (sensor_value / 1023) * 100
        # self.current_humidity = random.randint(41, 100) if sensor_value else random.randint(0, 40)
        if self.sprinkler_mode == self.SPRINKLER_AUTO:
            self.auto_regulate()
        self.save()

    def auto_regulate(self):
        # if self.use_forecast:
        # forecast = WeatherForecast.get_forecast_data(self.latitude, self.longitude)
        # if forecast and :
        # self.current_humidity += (forecast * 100 +
        if self.current_humidity < self.min_humidity:
            self.sprinkler_is_on = True
        elif self.current_humidity > self.max_humidity:
            self.sprinkler_is_on = False

    def blink(self):
        GPIO.output(int(self.blinker), True)
        time.sleep(settings.STATION_BLINKER_DELAY)
        GPIO.output(int(self.blinker), False)


class WeatherForecast(models.Model):
    """
    model representation of a WeatherForecast from darksky.net for a
    period of about an hour from the time of request.
    """
    time = models.DateTimeField(verbose_name='Time of Request')
    longitude = models.FloatField(verbose_name='Longitude')
    latitude = models.FloatField(verbose_name='latitude')
    data = JSONField()

    @staticmethod
    def get_forecast_data(latitude, longitude):
        one_hour_ago = datetime.now() - timedelta(hours=1)
        forecast = WeatherForecast.objects.filter(
            latitude=latitude, longitude=longitude,
            time__gt=one_hour_ago
        )
        if not forecast.exists():
            forecast = WeatherForecast.fetch_forecast(latitude, longitude)

        return forecast

    @staticmethod
    def fetch_forecast(latitude, longitude):
        url = 'https://api.darksky.net/forecast/fab40a14f74a4a8eb23444c6d0b161a1/6.5178,3.3827'
        headers = { 'cache-control': 'no-cache' }
        response = requests.request('GET', url, headers=headers)
        forecast = None
        if response.status_code == 200:
            response = json.loads(response.text)
            current_data = response['currently']
            forecast, created = WeatherForecast.objects.update_or_create(
                latitude=latitude, longitude=longitude,
                data=current_data, time=current_data.time
            )
        return forecast
