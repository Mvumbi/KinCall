from django import forms
from alert_core.models import Alert # Importation du modèle Alert
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from alert_core.models import CustomUser

class LoginForm(AuthenticationForm):
    """
    Formulaire simple basé sur AuthenticationForm de Django.
    Il ne nécessite pas de définition de champs si on utilise les champs par défaut
    (username et password).
    """
    class Meta:
        # Aucune méta-classe nécessaire pour AuthenticationForm
        pass

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Amélioration simple pour utiliser Tailwind CSS
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-red-500 focus:border-red-500',
                'placeholder': field.label
            })

class AlertForm(forms.ModelForm):
    
    # NOTE: Nous surchargeons la gestion des champs pour s'assurer
    # qu'ils correspondent aux inputs 'hidden' du JavaScript (latitude/longitude)

    class Meta:
        model = Alert
        fields = ['fire_type', 'photo', 'latitude', 'longitude', 'description']
        
        # Le champ 'description' est facultatif pour permettre un signalement très rapide
        widgets = {
            'fire_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-red-500 focus:border-red-500',
            }),
            'photo': forms.FileInput(attrs={
                'class': 'w-full text-sm text-gray-500',
                # Ajouté la classe 'text-sm' pour Tailwind
            }),
            'description': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-red-500 focus:border-red-500',
                'placeholder': _("Détails supplémentaires (ex: Piégé, danger électrique, adresse approximative...)"),
            }),
            
            # Les champs Latitude/Longitude sont masqués car remplis par JavaScript
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }

class CitizenRegistrationForm(UserCreationForm):
    # Ajout du champ de téléphone
    phone_number = forms.CharField(
        max_length=15, 
        required=False,
        label="Numéro de Téléphone (Optionnel)",
        widget=forms.TextInput(attrs={'placeholder': 'Ex: +243 999 000 000'})
    )

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        # On n'inclut pas le rôle, car il sera forcé à 'CITOYEN' dans la vue.
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Amélioration simple pour utiliser Tailwind CSS
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-red-500 focus:border-red-500',
            })