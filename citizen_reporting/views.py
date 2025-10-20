# citizen_reporting/views.py

from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import AlertForm, CitizenRegistrationForm, LoginForm
from django.contrib.auth.decorators import login_required
from alert_core.models import Alert




def register_view(request):
    """Gère le formulaire d'inscription pour les nouveaux citoyens."""
    
    if request.method == 'POST':
        form = CitizenRegistrationForm(request.POST)
        if form.is_valid():
            
            # 1. Sauvegarde l'utilisateur
            user = form.save(commit=False)
            
            # 2. Assignation forcée du rôle "CITOYEN"
            user.role = 'CITOYEN'
            user.save()
            
            messages.success(request, "Inscription réussie ! Vous pouvez maintenant vous connecter et signaler une urgence.")
            return redirect('login')
        
        # Si le formulaire n'est pas valide, les erreurs seront affichées automatiquement
        messages.error(request, "Erreur dans le formulaire. Veuillez vérifier vos informations.")
    else:
        # Affichage du formulaire vide
        form = CitizenRegistrationForm()

    return render(request, 'citizen_reporting/register.html', {'form': form})

# Vue pour rediriger la racine vers la page de connexion
def login_redirect(request):
    if request.user.is_authenticated:
        # Si l'utilisateur est déjà connecté, le rediriger selon son rôle
        return redirect_by_role(request.user)
    return redirect('login')


# 🎯 Vue du Formulaire de Signalement (Cible de la redirection citoyen)
def report_form_view(request):
    """Page contenant le formulaire de signalement d'incendie."""
    # Vous devrez ajouter @login_required ici
    
    # Logique de signalement et de géolocalisation à ajouter ici
    
    # Rendu du template principal de signalement (vous devrez créer citizen/report_form.html)
    return render(request, 'citizen/report_form.html', {})

# citizen_reporting/views.py (login_view)

def login_view(request):
    """
    Vue de connexion qui redirige les utilisateurs déjà connectés 
    pour éviter de revenir en arrière (problème de cache/UX).
    """

    # === 1. PROTECTION ANTI-RETOUR (GET ou POST) ===
    # Si l'utilisateur est déjà connecté, redirigez-le vers la page de redirection par défaut.
    if request.user.is_authenticated:
        # Utilisez settings.LOGIN_REDIRECT_URL (que vous devez avoir défini, ex: 'home')
        return redirect(settings.LOGIN_REDIRECT_URL or '/')

    # === 2. GESTION DU POST (Soumission du formulaire) ===
    if request.method == 'POST':
        # 🎯 CORRECTION : Passer l'objet 'request' au formulaire
        form = LoginForm(request=request, data=request.POST) 
        
        if form.is_valid():
            
            # 1. Récupération de l'utilisateur authentifié par le formulaire
            user = form.get_user()
            
            # 2. Connexion réussie et redirection
            login(request, user)
            messages.success(request, f"Bienvenue, {user.username}!")
            
            # Utilisation de votre logique de redirection par rôle
            return redirect_by_role(user)
            
        else:
            # Si form.is_valid() est False, le formulaire affichera les erreurs.
            pass # Laisse le flux continuer pour afficher le formulaire avec les erreurs
            
    # === 3. GESTION DU GET (Affichage initial du formulaire) ===
    else:
        form = LoginForm()

    # Affiche le formulaire de connexion
    return render(request, 'citizen_reporting/login.html', {'form': form})

# 🎯 Fonction d'aide à la redirection
def redirect_by_role(user):
    if user.role == 'POMPIER':
        # Redirection vers le tableau de bord des pompiers
        return redirect('dashboard_intervention') # Doit correspondre au name dans firefighter_dashboard/urls.py
    elif user.role == 'CITOYEN':
        # Redirection vers la page de signalement
        return redirect('citizen_report') # Doit correspondre au name dans citizen_reporting/urls.py
    # Fallback au cas où
    return redirect('login')


# Vue simple de déconnexion
def logout_view(request):
    logout(request)
    messages.info(request, "Vous êtes déconnecté.")
    return redirect('login')


@login_required
def report_form_view(request):
    """Gère l'affichage et la soumission du formulaire d'alerte."""
    
    # Vérification du rôle
    if request.user.role != 'CITOYEN':
        return redirect_by_role(request.user)

    if request.method == 'POST':
        form = AlertForm(request.POST, request.FILES)

        if form.is_valid():
            try:
                # 1. Création de l'objet Alert (non sauvegardé)
                alerte = form.save(commit=False)
                
                # 2. Assignation des champs gérés par le système
                alerte.reported_by = request.user
                alerte.status = 'NOUVEAU' 
                
                # 3. Sauvegarde finale
                alerte.save()

                messages.success(request, f"Alerte envoyée ! Nos équipes sont mobilisées. N° de suivi: #{alerte.id}.")
                
                # ----------------------------------------------------------------------
                # >>> CORRECTION PRINCIPALE : REDIRECTION AVEC L'ID DE L'ALERTE <<<
                # ----------------------------------------------------------------------
                return redirect('citizen_report_confirmation', alert_id=alerte.id) 
                
            except Exception as e:
                messages.error(request, f"Erreur serveur lors de la sauvegarde : {e}")
                print(f"Erreur lors de la sauvegarde de l'alerte: {e}") 
                
        else:
            # Erreurs de validation du formulaire
            messages.error(request, "Veuillez corriger les erreurs de validation (ex: Type d'incendie manquant ou localisation non reçue).")
    
    else:
        # Affichage initial du formulaire (méthode GET)
        form = AlertForm() 

    return render(request, 'citizen_reporting/report_form.html', {'form': form})


@login_required
def citizen_report_confirmation(request, alert_id):
    """Affiche la page de confirmation et les détails de l'alerte fraîchement soumise."""
    
    # REMARQUE : Assurez-vous d'avoir 'Alert' importé ou défini.
    # Dans un vrai projet, importez-le : from .models import Alert
    
    # On utilise get_object_or_404 pour récupérer l'alerte ou retourner une erreur 404
    # On vérifie également que seul l'utilisateur qui a soumis l'alerte peut la voir.
    try:
        # NOTE : Remplacez Alert par votre modèle réel si le nom est différent.
        alert = Alert.objects.get(id=alert_id, reported_by=request.user)
    except NameError:
        # Gérer le cas où le modèle Alert n'est pas importé (erreur de développement)
        messages.error(request, "Erreur : Le modèle Alert n'est pas importé dans la vue de confirmation.")
        # Redirection de sécurité
        return redirect('citizen_report')
    except Alert.DoesNotExist:
        messages.error(request, "Alerte introuvable ou vous n'êtes pas autorisé à la consulter.")
        return redirect('citizen_report')


    # Cette vue ne devrait pas traiter de requêtes POST. Elle est purement informative.
    return render(request, 'citizen_reporting/confirmation.html', {'alert': alert})


@login_required
def history_view(request):
    """
    Affiche l'historique de toutes les alertes soumises par l'utilisateur connecté.
    """
    # 1. Filtrer les alertes : seules celles où reported_by est l'utilisateur actuel
    user_alerts = Alert.objects.filter(reported_by=request.user).order_by('-reported_at')
    
    # 2. Rendre le template en passant la liste des alertes
    context = {
        'alerts': user_alerts,
        'alert_count': user_alerts.count()
    }
    return render(request, 'citizen_reporting/history.html', context)