from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('', views.analytics, name='analytics'),
    path('export/<str:model_name>/', views.export_csv, name='export_csv'),
]
