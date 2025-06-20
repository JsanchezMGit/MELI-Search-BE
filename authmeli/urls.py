# authmeli/urls.py
from django.urls import path
from .views import meli_callback

urlpatterns = [
    path("callback/", meli_callback),
]