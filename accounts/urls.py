from django.urls import path
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from . import views

def logout_view(request):
    logout(request)
    return redirect('login')

urlpatterns = [
    path('login/', LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', views.register, name='register'),
]
