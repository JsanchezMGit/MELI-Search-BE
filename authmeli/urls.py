# authmeli/urls.py
from django.urls import path
from .views import meli_callback, search_products

urlpatterns = [
    path("callback/", meli_callback),
    path("search/", search_products),
]