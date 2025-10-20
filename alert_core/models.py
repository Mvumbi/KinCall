from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

# ----------------------------------------------------------------------
# 1. MODÈLE D'UTILISATEUR (CUSTOMUSER)
# ----------------------------------------------------------------------

class CustomUser(AbstractUser):
    # Définition des Rôles
    ROLE_CHOICES = (
        ('CITOYEN', _('Citoyen Signaleur')),
        ('POMPIER', _('Sapeur-Pompier')),
    )
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='CITOYEN',
        verbose_name=_("Rôle de l'utilisateur")
    )
    
    # Rendre phone_number vraiment unique et optionnel
    phone_number = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        unique=True,
        verbose_name=_("Numéro de Téléphone")
    )

    class Meta:
        verbose_name = _("Utilisateur")
        verbose_name_plural = _("Utilisateurs")
        
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

# ----------------------------------------------------------------------
# 2. MODÈLE D'ALERTE INCENDIE (ALERT)
# ----------------------------------------------------------------------

class Alert(models.Model):
    # Choix des Statuts
    STATUS_CHOICES = (
        ('NOUVEAU', _('Nouveau Signalement')),
        ('EN_COURS', _('Intervention en Cours')),
        ('RÉSOLU', _('Résolu')),
        ('FAUSSE_ALERTE', _('Fausse Alerte')),
    )
    
    # Choix du Type d'Incendie (pour le SELECT du citoyen)
    FIRE_TYPE_CHOICES = (
        ('MAISON', _('Maison / Bâtiment')),
        ('MARCHÉ', _('Marché / Commerce')),
        ('VÉGÉTATION', _('Végétation / Brousse')),
        ('VÉHICULE', _('Véhicule')),
        ('AUTRE', _('Autre')),
    )

    # Données du Signalement
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Signalé par")
    )
    
    fire_type = models.CharField(
        max_length=50,
        choices=FIRE_TYPE_CHOICES,
        verbose_name=_("Type d'Incendie")
    )
    
    # 🛑 CORRECTION : Remplacement de gis_models.PointField par DecimalField 
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        verbose_name=_("Latitude GPS"),
        help_text=_("Coordonnée GPS Nord/Sud")
    )
    
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        verbose_name=_("Longitude GPS"),
        help_text=_("Coordonnée GPS Est/Ouest")
    )
    
    description = models.TextField(
        blank=True,
        verbose_name=_("Détails supplémentaires")
    )
    
    photo = models.ImageField(
        upload_to='alerts/',
        blank=True,
        null=True,
        verbose_name=_("Photo de l'incendie")
    )

    reported_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Heure du Signalement")
    )

    # Données de Gestion par les Pompiers
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='NOUVEAU',
        verbose_name=_("Statut de l'alerte")
    )

    assigned_firefighter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'role': 'POMPIER'}, 
        related_name='assigned_alerts',
        verbose_name=_("Pompier Assigné")
    )

    class Meta:
        verbose_name = _("Alerte Incendie")
        verbose_name_plural = _("Alertes Incendie")
        ordering = ['-reported_at']

    def __str__(self):
        return f"Alerte #{self.id} - {self.get_fire_type_display()} ({self.get_status_display()})"


# ----------------------------------------------------------------------
# 3. MODÈLE VÉHICULE (POUR LES RESSOURCES)
# ----------------------------------------------------------------------

class Vehicle(models.Model):

    VEHICLE_TYPE_CHOICES = (
        ('CCF', _('Camion-Citerne Feu de Forêt')),
        ('FPT', _('Fourgon Pompe Tonne')),
        ('VSAV', _('Ambulance')),
        ('AUTRE', _('Autre')),
    )

    STATUS_CHOICES = (
        ('DISPONIBLE', _('Disponible')),
        ('EN_MISSION', _('En Mission')),
        ('MAINTENANCE', _('Maintenance')),
    )

    name = models.CharField(
        max_length=100,
        verbose_name=_("Nom / Numéro du Véhicule"),
        unique=True
    )

    vehicle_type = models.CharField(
        max_length=50,
        choices=VEHICLE_TYPE_CHOICES,
        default='FPT',
        verbose_name=_("Type de Véhicule")
    )

    capacity = models.IntegerField(
        verbose_name=_("Capacité (Litres d'eau ou Places)"),
        null=True,
        blank=True
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='DISPONIBLE',
        verbose_name=_("Statut Opérationnel")
    )

    # 🛑 Position Géographique du véhicule (NON GeoDjango)
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        verbose_name=_("Dernière Latitude GPS")
    )
    
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        verbose_name=_("Dernière Longitude GPS")
    )
    
    last_update = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Dernière Mise à Jour")
    )

    class Meta:
        verbose_name = _("Véhicule d'Intervention")
        verbose_name_plural = _("Véhicules d'Intervention")

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"


# ----------------------------------------------------------------------
# 4. MODÈLE PROFIL POMPIER (POUR LES RESSOURCES)
# ----------------------------------------------------------------------

class FirefighterProfile(models.Model):
    RANK_CHOICES = (
        ('CHEF', 'Chef d’équipe'),
        ('LIEUTENANT', 'Lieutenant'),
        ('CAPORAL', 'Caporal'),
        ('SAPEUR', 'Sapeur'),
    )

    SHIFT_CHOICES = (
        ('EN_SERVICE', 'En Service'),
        ('EN_REPOS', 'En Repos'),
        ('EN_PAUSE', 'En Pause'),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'POMPIER'},
        verbose_name=_("Agent Pompier")
    )
    
    rank = models.CharField(
        max_length=20,
        choices=RANK_CHOICES,
        default='SAPEUR',
        verbose_name=_("Grade")
    )
    
    shift_status = models.CharField(
        max_length=20,
        choices=SHIFT_CHOICES,
        default='EN_REPOS',
        verbose_name=_("Statut de Service")
    )

    assigned_vehicle = models.ForeignKey(
        Vehicle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Véhicule Assigné")
    )

    class Meta:
        verbose_name = _("Profil Pompier")
        verbose_name_plural = _("Profils Pompiers")

    def __str__(self):
        return f"Profil de {self.user.username}"