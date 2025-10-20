from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

# Importation des vues d'authentification de Django et de votre application
from citizen_reporting import views as citizen_views

urlpatterns = [
    path('', citizen_views.login_redirect, name='home'), 
    path('admin/', admin.site.urls),
     path('accounts/', include([
        # Le chemin "accounts/login/" est maintenant trouvé
        path('login/', citizen_views.login_view, name='login'), # Remplacez views.login_view par votre fonction de vue
        # Le chemin "accounts/logout/" est maintenant trouvé
        path('logout/', citizen_views.logout_view, name='logout'), # Remplacez views.logout_view par votre fonction de vue
    ])),
    # Inclusion des routes spécifiques à chaque application
    path('citoyen/', include('citizen_reporting.urls')),
    path('pompiers/', include('firefighter_dashboard.urls')),
    path('api/', include('alert_core.urls')),
]
if settings.DEBUG:
    # Servez les fichiers médias
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Servez les fichiers statiques collectés (Admin CSS/JS)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)