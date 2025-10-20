# firefighter_dashboard/views.py (NOUVEAU FICHIER)

from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from alert_core.models import Alert, Vehicle, FirefighterProfile, CustomUser
from django.db.models import Q
import json
from django.core.serializers import serialize
from django.contrib import messages # Pour les notifications utilisateur
from django.utils import timezone


def is_firefighter(user):
    """Vérifie si l'utilisateur est authentifié et a le rôle 'POMPIER'."""
    # Note : Le CustomUser est déjà importé via FirefighterProfile/Alert
    return user.is_authenticated and user.role == 'POMPIER'

@login_required
@user_passes_test(is_firefighter, login_url='/login/')
def alert_details_view(request, alert_id):
    """Page de gestion détaillée d'une alerte."""
    alert = get_object_or_404(Alert, id=alert_id)
    firefighter_profile = get_object_or_404(FirefighterProfile, user=request.user)

    if request.method == 'POST':
        action = request.POST.get('action')
        new_status = request.POST.get('new_status')

        # ----------------------------------------------------
        # ACTION 1: PRENDRE EN CHARGE (Take Over)
        # ----------------------------------------------------
        if action == 'take_over':
            # Vérifier si l'alerte n'est pas déjà assignée ou est assignée à l'utilisateur actuel
            if not alert.assigned_firefighter or alert.assigned_firefighter == request.user:
                alert.assigned_firefighter = request.user
                alert.status = 'EN_COURS' # Changer le statut à EN_COURS
                alert.started_at = timezone.now()
                alert.save()
                messages.success(request, f"Vous avez pris en charge l'alerte #{alert_id}.")
            else:
                messages.error(request, f"Cette alerte est déjà gérée par {alert.assigned_firefighter.username}.")
            return redirect('alert_details', alert_id=alert.id)

        # ----------------------------------------------------
        # ACTION 2: CHANGER DE STATUT (Close/Resolve)
        # ----------------------------------------------------
        elif action == 'change_status' and new_status in [s[0] for s in Alert.STATUS_CHOICES]:
            
            # Assurez-vous que seul le pompier assigné peut la clôturer
            if alert.assigned_firefighter != request.user:
                 messages.error(request, "Vous devez être assigné à cette alerte pour en changer le statut.")
                 return redirect('alert_details', alert_id=alert.id)
            
            alert.status = new_status
            
            if new_status in ['RESOLU', 'FAUSSE_ALERTE']:
                alert.resolved_at = timezone.now()
            
            alert.save()
            messages.success(request, f"Le statut de l'alerte #{alert_id} a été mis à jour à '{alert.get_status_display()}'.")
            
            # Après résolution, redirection vers le dashboard pour voir la liste propre
            if new_status in ['RESOLU', 'FAUSSE_ALERTE']:
                return redirect('dashboard_intervention') 
            
            return redirect('alert_details', alert_id=alert.id)

    # Contexte pour le GET
    context = {
        'alert': alert,
        'firefighter_profile': firefighter_profile,
        # Pour les boutons de changement de statut
        'status_choices': [
            {'code': 'RESOLU', 'display': 'Résolue', 'color': 'green'},
            {'code': 'FAUSSE_ALERTE', 'display': 'Fausse Alerte', 'color': 'red'},
        ]
    }
    
    return render(request, 'dashboard/alert_details.html', context)

@login_required
@user_passes_test(is_firefighter, login_url='/login/')
def intervention_view(request):
    """Tableau de bord principal : Liste des alertes actives + données carte."""

    active_statuses = ['NOUVEAU', 'EN_COURS']
    
    alerts_queryset = Alert.objects.filter(
        status__in=active_statuses
    ).order_by('-reported_at') 

    # 1. Préparation des données pour la carte (JSON)
    alerts_list = []
    for alert in alerts_queryset:
        alerts_list.append({
            'id': alert.id,
            'latitude': str(alert.latitude),
            'longitude': str(alert.longitude),
            'status': alert.status,
            'status_display': alert.get_status_display(),
            'fire_type_display': alert.get_fire_type_display(),
            'assigned_firefighter': alert.assigned_firefighter.username if alert.assigned_firefighter else 'Aucun',
        })
        
    alerts_json = json.dumps(alerts_list) # Sérialisation en chaîne JSON

    context = {
        'alerts': alerts_queryset,
        'alert_count': alerts_queryset.count(),
        'alerts_json': alerts_json, # ⬅️ Passage du JSON au template
    }
    
    return render(request, 'dashboard/intervention.html', context)

@login_required
@user_passes_test(is_firefighter, login_url='/login/')
def resources_view(request):
    """Affiche la liste des véhicules et des agents (Pompiers) de l'entreprise."""

    # 1. Récupérer tous les véhicules, triés par statut (Disponible en premier)
    vehicles = Vehicle.objects.all().order_by('status')

    # 2. Récupérer les profils des pompiers actifs
    # Utiliser select_related pour récupérer le CustomUser et le Véhicule assigné en une seule requête
    firefighters_profiles = FirefighterProfile.objects.select_related(
        'user', 
        'assigned_vehicle'
    ).filter(
        user__is_active=True # S'assurer que les comptes ne sont pas désactivés
    ).order_by('rank', 'shift_status')


    context = {
        'vehicles': vehicles,
        'firefighters': firefighters_profiles,
    }
    
    return render(request, 'firefighter_dashboard/resources.html', context)

@login_required
def profile_view(request):
    """Affichage du profil de l'agent connecté."""
    # Logique d'affichage des détails de l'utilisateur/profil à ajouter ici.
    return render(request, 'dashboard/profile.html', {})

# Pour l'étape de test, vous pouvez ajouter une page d'accueil simple si nécessaire
@login_required
def dashboard_home(request):
    """Page d'accueil du tableau de bord des pompiers."""
    return redirect('dashboard_intervention')


# Fonction pour vérifier si l'utilisateur est un pompier (à réutiliser dans toutes les vues du dashboard)
def is_firefighter(user):
    return user.is_authenticated and user.role == 'POMPIER'

# 🎯 Vue d'Intervention (Accueil Pompier)
@login_required
@user_passes_test(is_firefighter, login_url='/login/') # S'assure que seul un Pompier y accède
def intervention_view(request):
    """Tableau de bord principal : Liste des alertes actives."""

    # Récupérer les alertes qui ne sont ni Résolues ni de Fausses Alertes
    active_statuses = ['NOUVEAU', 'EN_COURS']
    
    alerts = Alert.objects.filter(
        status__in=active_statuses
    ).order_by('-reported_at') # Les plus récentes d'abord

    context = {
        'alerts': alerts,
        'alert_count': alerts.count()
    }

    return render(request, 'firefighter_dashboard/intervention.html', context)


# 🎯 Vue pour les détails d'une alerte (à créer pour le lien "Voir & Gérer")
@login_required
@user_passes_test(is_firefighter, login_url='/login/')
def alert_details_view(request, alert_id):
    """Page de gestion détaillée d'une alerte."""
    alert = get_object_or_404(Alert, id=alert_id)
    # Logique de gestion : changement de statut, assignation de véhicule, etc.
    return render(request, 'firefighter_dashboard/alert_details.html', {'alert': alert})

@login_required
@user_passes_test(is_firefighter, login_url='/login/')
def profile_view(request):
    """Affiche le profil détaillé du pompier connecté."""
    
    # Récupère le profil Pompier (y compris les relations avec user et assigned_vehicle)
    try:
        profile = FirefighterProfile.objects.select_related('user', 'assigned_vehicle').get(user=request.user)
    except FirefighterProfile.DoesNotExist:
        profile = None # Gérer le cas où le profil n'existe pas (improbable après initialisation)

    context = {
        'profile': profile,
    }
    
    return render(request, 'firefighter_dashboard/profile.html', context)


def is_firefighter(user):
    # Assurez-vous que le champ 'role' existe sur votre modèle User
    return user.is_authenticated and user.role == 'POMPIER'

@login_required
@user_passes_test(is_firefighter, login_url='/access-denied/')
def alert_action_view(request, alert_id):
    """
    Gère les actions POST sur une alerte (changement de statut, assignation, prise en charge).
    """
    alert = get_object_or_404(Alert, id=alert_id)

    if request.method == 'POST':
        # On lit le champ 'action' (envoyé par votre formulaire 'take_over')
        action_name = request.POST.get('action') 
        
        # On lit le champ 'action_type' (utilisé par la logique générique de status)
        action_type = request.POST.get('action_type')

        # --- LOGIQUE 1 : PRISE EN CHARGE (Take Over) ---
        if action_name == 'take_over' and alert.status == 'NOUVEAU':
            # Si l'alerte est NOUVEAU, le pompier prend en charge l'intervention
            alert.assigned_firefighter = request.user
            alert.status = 'EN_COURS'
            alert.save()
            
        # --- LOGIQUE 2 : CHANGEMENT DE STATUT GÉNÉRIQUE (pour les autres formulaires) ---
        elif action_type == 'update_status':
            new_status = request.POST.get('status')
            # Optionnel : Ajoutez une vérification que seul le pompier assigné peut mettre à jour
            # if alert.assigned_firefighter == request.user:
            if new_status in [status[0] for status in Alert.STATUS_CHOICES]:
                alert.status = new_status
                alert.save()
            
        # --- LOGIQUE 3 : ASSIGNATION/DÉSASSIGNATION MANUELLE ---
        elif action_type == 'assign_self':
            if alert.assigned_firefighter == request.user:
                # Se désassigner si déjà assigné
                alert.assigned_firefighter = None
            else:
                # S'assigner l'alerte
                alert.assigned_firefighter = request.user
            alert.save()

        # Rediriger vers la page de détail après l'action
        return redirect('alert_details', alert_id=alert.id) 
        
    # Si la méthode n'est pas POST, on redirige simplement
    return redirect('alert_details', alert_id=alert.id)
