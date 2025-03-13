from .views import RegisterationView,UserNameValidationView,EmailValidationView,VerificationView,LoginView,LogoutView,RequestPasswordResetEmail,CompletePasswordReset
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('register', RegisterationView.as_view(), name="register"),
    path('login', LoginView.as_view(), name="login"),
    path('logout', LogoutView.as_view(), name="logout"),
    path('validates-username', csrf_exempt(UserNameValidationView.as_view()), name="validates-username"),
    path('validates_email', csrf_exempt(EmailValidationView.as_view()),name='validates_email'),
    path('activate/<uidb64>/<token>',VerificationView.as_view(),name="active"),
    path('set-newpassword/<uidb64>/<token>',CompletePasswordReset.as_view(),name="reset-user-password"),
    path('request-reset-link',RequestPasswordResetEmail.as_view(),name="request-password"),
]
