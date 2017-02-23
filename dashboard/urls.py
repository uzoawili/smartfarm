from django.conf.urls import url
from django.contrib.auth.views import logout_then_login
from .views import (
    IndexView, LoginView, CreateUserView, StationsView,
    StationSetupView, StationSettingsView
)

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    url(r'^logout/$', logout_then_login, name='logout'),
    url(r'^create-user/$', CreateUserView.as_view(), name='create_user'),
    url(r'^stations/$', StationsView.as_view(), name='stations'),
    url(r'^stations/setup/$', StationSetupView.as_view(), name='station_setup'),
    url(r'^stations/(?P<pk>[0-9]+)/settings/$', StationSettingsView.as_view(), name='station_settings'),
]