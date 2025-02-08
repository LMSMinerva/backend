from django.urls import path
from rest_framework_simplejwt.views import TokenVerifyView
from .views.views import LoginWithGoogle, LogoutView


urlpatterns = [
    path("login-with-google/", LoginWithGoogle.as_view(), name="login-with-google"),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token-verify/', TokenVerifyView.as_view(), name='token-verify'),
]
