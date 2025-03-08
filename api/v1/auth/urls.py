from django.urls import path

from .views import google_auth_callback


urlpatterns = [
    path("google/callback/", google_auth_callback, name="google-callback"),
]
