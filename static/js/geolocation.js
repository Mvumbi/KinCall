// static/js/geolocation.js

const latInput = document.getElementById('id_latitude');
const longInput = document.getElementById('id_longitude');
const statusText = document.getElementById('geo-status');
const submitButton = document.getElementById('submit-button');

// Désactiver le bouton de soumission au départ pour forcer la localisation
submitButton.disabled = true;
submitButton.textContent = 'Localisation en cours...';

// 1. Fonction appelée en cas de succès de la géolocalisation
function positionSuccess(position) {
    const lat = position.coords.latitude;
    const long = position.coords.longitude;

    // Remplir les champs cachés avec les coordonnées
    latInput.value = lat;
    longInput.value = long;

    // Mettre à jour le statut et activer le bouton
    statusText.className = 'text-center text-sm text-green-600 font-semibold p-1';
    statusText.textContent = `Statut : Localisation OK ✅ (Lat: ${lat.toFixed(4)}, Long: ${long.toFixed(4)}). Prêt à alerter.`;
    
    submitButton.textContent = '🚨 ALERTER LES POMPIERS MAINTENANT';
    submitButton.disabled = false;
}

// 2. Fonction appelée en cas d'erreur de la géolocalisation
function positionError(error) {
    statusText.className = 'text-center text-sm text-red-600 font-bold p-1 bg-red-100 rounded-lg';
    submitButton.disabled = true; // Le bouton doit rester désactivé si la localisation est requise.

    let message = "⚠️ Erreur de localisation : ";
    if (error.code === 1) {
        // PERMISSION_DENIED
        message += "Veuillez autoriser l'accès à votre position GPS. Le bouton d'alerte est désactivé.";
    } else if (error.code === 2) {
        // POSITION_UNAVAILABLE
        message += "Impossible de déterminer votre position. Veuillez vérifier vos paramètres GPS.";
    } else if (error.code === 3) {
        // TIMEOUT
        message += "Temps d'attente dépassé. Réessayez ou déplacez-vous vers une zone avec un meilleur signal.";
    } else {
        message += "Une erreur inconnue s'est produite. La soumission est bloquée.";
    }
    statusText.textContent = message;
}

// 3. Lancer la demande de géolocalisation au chargement
if (navigator.geolocation) {
    statusText.textContent = "Statut : Localisation en cours...";
    navigator.geolocation.getCurrentPosition(positionSuccess, positionError, {
        enableHighAccuracy: true, // Haute précision préférée
        timeout: 15000, // 15 secondes
        maximumAge: 0 // Ne pas utiliser de données mises en cache
    });
} else {
    statusText.className = 'text-center text-sm text-red-600 font-bold p-1 bg-red-100 rounded-lg';
    statusText.textContent = "Votre navigateur ne supporte pas la géolocalisation. Impossible d'envoyer l'alerte.";
    submitButton.disabled = true;
}