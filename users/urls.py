from django.urls import path
from .views.views import LoginWithGoogle, LogoutView, DocumentedTokenVerifyView
from .views.views2 import EmailSignup, EmailLogin

urlpatterns = [
    path("login-with-google/", LoginWithGoogle.as_view(), name="login-with-google"),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token-verify/', DocumentedTokenVerifyView.as_view(), name='token-verify'),
    path("sign-up-with-email/", EmailSignup.as_view(), name="sign-up-with-email"),
    path("login-with-email/", EmailLogin.as_view(), name="login-with-email")
]
