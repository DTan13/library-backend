from django.urls import path

from api import views
from api import auth

urlpatterns = [
    path("", views.index),
    path("signup/", auth.signup),
    path("login/", auth.login),
    path("books/", views.books),
]
