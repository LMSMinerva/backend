from django.urls import path
from .views.views import LoginWithGoogle, LogoutView, DocumentedTokenVerifyView

urlpatterns = [
    path("login-with-google/", LoginWithGoogle.as_view(), name="login-with-google"),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token-verify/', DocumentedTokenVerifyView.as_view(), name='token-verify'),
]
