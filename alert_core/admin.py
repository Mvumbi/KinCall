from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Alert, Vehicle, FirefighterProfile
from django.utils.translation import gettext_lazy as _

# ----------------------------------------------------------------------
# 1. Configuration du Profil Pompier (Inline)
# ----------------------------------------------------------------------

# Permet d'éditer le profil pompier directement dans la page de l'utilisateur.
class FirefighterProfileInline(admin.StackedInline):
    model = FirefighterProfile
    can_delete = False
    verbose_name_plural = _('Profil Pompier (pour les agents)')
    fieldsets = (
        (None, {'fields': ('rank', 'shift_status', 'assigned_vehicle')}),
    )

# ----------------------------------------------------------------------
# 2. Configuration de CustomUser dans l'Admin
# ----------------------------------------------------------------------

class CustomUserAdmin(UserAdmin):
    # Ajoute 'role' et 'phone_number' à la liste des champs affichés
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'phone_number', 'is_staff')
    
    # Ajoute 'role' et 'phone_number' aux champs de recherche
    search_fields = ('username', 'email', 'phone_number')
    
    # Filtres rapides
    list_filter = ('role', 'is_staff', 'is_active')
    
    # Réorganisation du formulaire d'édition
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone_number')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        (_('Rôle dans le système'), {'fields': ('role',)}), # Champ rôle ajouté
    )
    
    # Utilisation du profil pompier uniquement si le rôle est 'POMPIER'
    def get_inline_instances(self, request, obj=None):
        if not obj or obj.role != 'POMPIER':
            return []
        return [FirefighterProfileInline(self.model, self.admin_site)]
    
# Enregistrement du modèle CustomUser (remplace l'enregistrement par défaut)
admin.site.register(CustomUser, CustomUserAdmin)

# Suppression de l'enregistrement par défaut pour le profil pompier si on l'utilise uniquement en inline
# admin.site.register(FirefighterProfile) 


# ----------------------------------------------------------------------
# 3. Configuration des Alertes (Alert)
# ----------------------------------------------------------------------

class AlertAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'reported_at', 'status', 'fire_type', 
        'reported_by_username', 'assigned_firefighter', 
        'latitude', 'longitude', 'has_photo'
    )
    
    # Rendre les champs clés éditables directement dans la liste
    list_editable = ('status', 'assigned_firefighter')
    
    # Filtres
    list_filter = ('status', 'fire_type', 'reported_at', 'assigned_firefighter')
    
    # Champs de recherche
    search_fields = (
        'description', 'reported_by__username', 'assigned_firefighter__username', 
        'latitude', 'longitude'
    )
    
    # Groupement des champs dans le formulaire d'édition
    fieldsets = (
        (_('Informations de Signalement'), {
            'fields': ('reported_by', 'reported_at', 'fire_type', 'description', 'photo'),
        }),
        (_('Localisation GPS'), {
            # Les champs de localisation sont en lecture seule pour éviter les erreurs de saisie manuelle
            'fields': (('latitude', 'longitude'),),
        }),
        (_('Gestion de l\'Intervention'), {
            'fields': ('status', 'assigned_firefighter'),
        }),
    )

    # Afficher le nom d'utilisateur du signaleur
    def reported_by_username(self, obj):
        return obj.reported_by.username if obj.reported_by else _("Anonyme / Supprimé")
    reported_by_username.short_description = _("Signalé par")
    
    # Indiquer rapidement si une photo est présente
    def has_photo(self, obj):
        return bool(obj.photo)
    has_photo.boolean = True
    has_photo.short_description = _("Photo ?")

    # Rendre les champs de signalement en lecture seule après la création
    readonly_fields = ('reported_by', 'reported_at', 'latitude', 'longitude')
    
    # Actions personnalisées (ex: Marquer comme Résolu)
    actions = ['mark_resolved', 'mark_in_progress']
    
    def mark_resolved(self, request, queryset):
        queryset.update(status='RÉSOLU')
        self.message_user(request, _(f"{queryset.count()} alertes marquées comme Résolues."))
    mark_resolved.short_description = _("Marquer comme 'Résolu'")
    
    def mark_in_progress(self, request, queryset):
        queryset.update(status='EN_COURS')
        self.message_user(request, _(f"{queryset.count()} alertes marquées comme 'Intervention en Cours'."))
    mark_in_progress.short_description = _("Marquer comme 'Intervention en Cours'")

admin.site.register(Alert, AlertAdmin)


# ----------------------------------------------------------------------
# 4. Configuration des Véhicules (Vehicle)
# ----------------------------------------------------------------------

class VehicleAdmin(admin.ModelAdmin):
    list_display = ('name', 'vehicle_type', 'capacity', 'status', 'last_update')
    list_editable = ('status',)
    list_filter = ('vehicle_type', 'status')
    search_fields = ('name',)
    
    fieldsets = (
        (None, {'fields': ('name', 'vehicle_type', 'capacity', 'status')}),
        (_("Localisation et Mise à Jour (Automatique)"), {
            # Ces champs sont généralement mis à jour par une API, donc en lecture seule dans l'admin
            'fields': (('latitude', 'longitude'), 'last_update'),
            'classes': ('collapse',),
        }),
    )
    
    readonly_fields = ('latitude', 'longitude', 'last_update')

admin.site.register(Vehicle, VehicleAdmin)
