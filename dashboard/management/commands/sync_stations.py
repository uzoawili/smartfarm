import threading
import time

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from dashboard.models import Station


class Command(BaseCommand):
    help = 'starts a process that periodically syncs the state of each station with the physical device.'

    def handle(self, *args, **options):
        # thread_name = settings.STATION_IO_SYNC['thread_name']
        # thread = get_thread_by_name(thread_name)
        # if thread is None:
        #     thread = threading.Thread(
        #         name=settings.STATION_IO_SYNC.get(thread_name),
        #         target=self.sync_stations_with_IO, args=())
        # thread.start()  # Start the execution
        self.sync_stations_with_IO()

    def sync_stations_with_IO(self):
        while True:
            for station in Station.objects.all():
                try:
                    station.sync_with_io()
                    self.stdout.write('Station {}: {} successfully synced. CH={} SIO={}'.format(
                        station.pk, station.name, station.current_humidity, station.sprinkler_is_on))
                except Exception as e:
                    # self.stdout.write(str(e))
                    raise e
            time.sleep(settings.STATION_IO_SYNC.get('interval', 5))

def get_thread_by_name(name):
    for t in threading.enumerate():
        if t.name == name and t.is_alive():
            return t
    return None
