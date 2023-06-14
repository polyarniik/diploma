from django.contrib.auth.views import LogoutView
from django.urls import path

from users import views

app_name = "users"

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="/"), name="logout"),
    path("register/", views.RegistrationView.as_view(), name="register"),
]
