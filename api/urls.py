from django.urls import path

from api import views
from api import auth

urlpatterns = [
    path("", views.index),
    path("me/", auth.me),
    path("signup/", auth.signup),
    path("login/", auth.login),
    path("logout/", auth.logout),
    path("books/", views.books),
]
