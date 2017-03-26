from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseBadRequest

from .models import Station
from .forms import StationSettingsForm, StationStateForm


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, **kwargs):
        view = super(LoginRequiredMixin, cls).as_view(**kwargs)
        return login_required(view)

class IndexView(View):

    def get(self, request, *args, **kwargs):
        if User.objects.filter(is_staff=True).exists():
            return redirect('dashboard:login')

        return redirect('dashboard:create_user')


class CreateUserView(View):

    def get(self, request, *args, **kwargs):
        if User.objects.filter(is_staff=True).exists():
            return redirect('dashboard:login')
        return render(request, 'dashboard/create_user.html', {'form': UserCreationForm()})

    def post(self, request, *args, **kwargs):
        """
        Handles the create user form submission
        """
        form = UserCreationForm(request.POST)
        if form.is_valid():
            # Save the form to add the new user to db
            user = form.save(commit=False)
            user.is_staff = user.is_active = True
            user.save()
            # get the auth details, authenticate & log the user in
            username = form['username'].value()
            password = form['password1'].value()
            authenticated_user = authenticate(username=username, password=password)
            login(self.request, authenticated_user)
            # redirect to the stations view
            return redirect('dashboard:stations')
        # re-render the form (with any errors)
        return render(request, 'dashboard/create_user.html', {'form': form})


class LoginView(View):

    def get(self, request, *args, **kwargs):
        if not User.objects.filter(is_staff=True).exists():
            return redirect('dashboard:create_user')
        return render(request, 'dashboard/login.html', {'form': AuthenticationForm()})

    def post(self, request, *args, **kwargs):
        """
        Handles the create user form submission
        """
        form = AuthenticationForm(None, request.POST)
        if form.is_valid():
            # get the auth details, authenticate & log the user in
            username = form['username'].value()
            password = form['password'].value()
            user = authenticate(username=username, password=password)
            login(self.request, user)
            # redirect to the stations view
            return redirect('dashboard:stations')
        # re-render the form (with any errors)
        return render(request, 'dashboard/login.html', {'form': form})


class StationsView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        stations = Station.objects.all()
        context = {
            'stations': stations,
        }
        return render(request, 'dashboard/stations.html', context)


class StationSetupView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        return render(request, 'dashboard/station_settings.html', {'form': StationSettingsForm()})

    def post(self, request, *args, **kwargs):
        """
        Handles the create user form submission
        """
        form = StationSettingsForm(request.POST)
        if form.is_valid():
            # Save the form to add the station to db
            form.save()
            # redirect to the stations view
            return redirect('dashboard:stations')
        # re-render the form (with any errors)
        return render(request, 'dashboard/station_settings.html', {'form': form})


class StationSettingsView(LoginRequiredMixin, View):

    def get(self, request, *args, **kwargs):
        station = get_object_or_404(Station, pk=kwargs.get('pk'))
        context = {'form': StationSettingsForm(instance=station)}
        return render(request, 'dashboard/station_settings.html', context)

    def post(self, request, *args, **kwargs):
        """
        Handles the create user form submission
        """
        station = get_object_or_404(Station, pk=kwargs.get('pk'))
        form = StationSettingsForm(request.POST, instance=station)
        if form.is_valid():
            # Save the form to add the station to db
            form.save()
            # redirect to the stations view
            return redirect('dashboard:stations')
        # re-render the form (with any errors)
        return render(request, 'dashboard/station_settings.html', {'form': form})


class StationStateUpdateView(LoginRequiredMixin, View):

    def post(self, request, *args, **kwargs):
        """
        """
        station = get_object_or_404(Station, pk=kwargs.get('pk'))
        form = StationStateForm(request.POST, instance=station)
        if form.is_valid():
            # Save the form to update the station in db
            station = form.save()
            # get and return the new station state as JSON:
            return JsonResponse(station.getState())

        # return a bad request error response:
        return HttpResponseBadRequest()


