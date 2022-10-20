from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView

from .views import homepage, register

urlpatterns = [
    path('home/', homepage, name='homepage'),

    path('', LoginView.as_view(template_name='home/registration/login.html'), name='login_url'),
    path('logout/', LogoutView.as_view(), name='logout_url'),
    path('register/', register, name='register_url')
]