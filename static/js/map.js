// firefighter_dashboard/static/js/map.js

document.addEventListener('DOMContentLoaded', function() {
    const mapElement = document.getElementById('mapid');
    if (!mapElement) return;

    // 1. Initialisation de la carte Leaflet
    // Coordonnées approximatives de Kinshasa (centre)
    const KINSHASA_CENTER = [-4.3224, 15.3070]; 
    const initialZoom = 12; // Zoom initial, pour voir une bonne partie de la ville

    const map = L.map('mapid').setView(KINSHASA_CENTER, initialZoom);

    // Ajout d'une couche de tuiles OpenStreetMap (OSM)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    // 2. Récupération des données d'alerte de Django (via le bloc JSON)
    const dataScript = document.getElementById('alert-data');
    if (!dataScript) return;
    
    let alerts = [];
    try {
        // Le contenu du bloc JSON est sécurisé par |safe dans Django
        alerts = JSON.parse(dataScript.textContent);
    } catch (e) {
        console.error("Erreur de parsing des données d'alerte JSON:", e);
        return;
    }

    // 3. Création d'icônes personnalisées pour les alertes
    const FireIcon = L.icon({
        iconUrl: "{% static 'img/fire_icon.png' %}", // Vous devrez ajouter cette image
        iconSize: [32, 37],
        iconAnchor: [16, 37],
        popupAnchor: [0, -30]
    });
    
    // 4. Parcourir les alertes et placer les marqueurs
    alerts.forEach(alert => {
        const lat = parseFloat(alert.latitude);
        const lon = parseFloat(alert.longitude);

        if (isNaN(lat) || isNaN(lon)) {
            console.warn(`Alerte #${alert.id} a des coordonnées invalides.`);
            return;
        }
        
        // Choisir la couleur de l'icône en fonction du statut
        let iconColor = (alert.status === 'NOUVEAU') ? 'red' : 'orange';

        // Contenu du Pop-up
        const popupContent = `
            <div class="font-bold text-red-700">🚨 ALERTE #${alert.id}</div>
            <p>Type: ${alert.fire_type_display}</p>
            <p>Statut: <span style="color:${iconColor};">${alert.status_display}</span></p>
            <p>Assigné: ${alert.assigned_firefighter || 'Aucun'}</p>
            <a href="/pompiers/intervention/${alert.id}/" class="text-blue-500 hover:underline">Gérer l'intervention</a>
        `;

        // Créer le marqueur
        L.marker([lat, lon], {
            icon: FireIcon // Utilisez l'icône de feu pour une meilleure visibilité
        })
        .addTo(map)
        .bindPopup(popupContent);
    });
    
    // 5. Ajuster la vue de la carte pour englober toutes les alertes (si il y en a)
    if (alerts.length > 0) {
        const latLons = alerts.map(a => [parseFloat(a.latitude), parseFloat(a.longitude)]);
        const bounds = L.latLngBounds(latLons);
        map.fitBounds(bounds.pad(0.5)); // Ajouter un petit padding
    }
});