# firefighter_dashboard/urls.py

from django.urls import path
from . import views

urlpatterns = [
   # Dashboard / Intervention (cible de la redirection 'POMPIER')
    path('', views.intervention_view, name='dashboard_intervention'),
    
    # Détails et Gestion d'une alerte spécifique
    path('intervention/<int:alert_id>/', views.alert_details_view, name='alert_details'),
    
    # Ressources
    path('resources/', views.resources_view, name='dashboard_resources'),
    
    path('intervention/<int:alert_id>/action/', views.alert_action_view, name='alert_action'), 
    # Profil
    path('profil/', views.profile_view, name='dashboard_profile'),
]