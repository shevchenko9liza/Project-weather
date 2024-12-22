function initMap(locations) {
    const map = L.map('map').setView([55.7558, 37.6173], 5);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
    
    locations.forEach(location => {
        L.marker([location.lat, location.lon])
         .bindPopup(`
            <b>${location.name}</b><br>
            Температура: ${location.temp}°C<br>
            Влажность: ${location.humidity}%<br>
            Ветер: ${location.wind} км/ч
         `)
         .addTo(map);
    });
} 