from django.conf.urls import url
from django.contrib.auth.views import logout_then_login
from .views import IndexView, LoginView, CreateUserView, StationsView

urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'^login\/?$', LoginView.as_view(), name='login'),
    url(r'^logout\/?$', logout_then_login, name='logout'),
    url(r'^create-user\/?$', CreateUserView.as_view(), name='create_user'),
    url(r'^stations\/?$', StationsView.as_view(), name='stations'),
]