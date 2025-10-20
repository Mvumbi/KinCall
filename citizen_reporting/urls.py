# citizen_reporting/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('alerte/', views.report_form_view, name='citizen_report'), 
    
    
    path('register/', views.register_view, name='citizen_register'), 
    path('history/', views.history_view, name='history'),
    path('alerte/confirmation/<int:alert_id>/', views.citizen_report_confirmation, name='citizen_report_confirmation'),
]