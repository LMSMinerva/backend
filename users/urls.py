from django.urls import path
from rest_framework_simplejwt.views import TokenVerifyView
from .views import LoginWithGoogle


urlpatterns = [
    path("login-with-google/", LoginWithGoogle.as_view(), name="login-with-google"),
    path('token-verify/', TokenVerifyView.as_view(), name='token-verify'),

]
