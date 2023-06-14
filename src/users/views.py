from django.contrib.auth import get_user_model, views
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import generic

User = get_user_model()


# Create your views here.


class LoginView(views.LoginView):
    template_name = "users/login.html"
    redirect_authenticated_user = True
    success_url = reverse_lazy("repositories:repository_list")


class RegistrationView(generic.CreateView):
    pass
