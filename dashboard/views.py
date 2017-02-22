from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


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


class StationsView(View):

    def get(self, request, *args, **kwargs):
        return render(request, 'dashboard/stations.html', {})
