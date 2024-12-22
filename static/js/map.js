function initMap(locations) {
    const map = L.map('map').setView([55.7558, 37.6173], 5);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);
    
    // Создаем группу маркеров
    var markers = L.featureGroup();
    
    // Создаем массив точек для построения маршрута
    var routePoints = [];
    
    locations.forEach((location, index) => {
        // Добавляем маркер с информацией о погоде
        const marker = L.marker([location.coordinates.lat, location.coordinates.lon])
            .bindPopup(`
                <div class="popup-content">
                    <h3>${location.location}</h3>
                    <div class="weather-info">
                        <p><i class="fas fa-thermometer-half"></i> Температура: ${location.weather.temp}°C</p>
                        <p><i class="fas fa-tint"></i> Влажность: ${location.weather.humidity}%</p>
                        <p><i class="fas fa-wind"></i> Ветер: ${location.weather.wind_speed} км/ч</p>
                        <p><i class="fas fa-cloud-rain"></i> Вероятность осадков: ${location.weather.rain_prob}%</p>
                    </div>
                    ${location.weather.is_bad ? 
                        `<div class="weather-warning">${location.weather.message}</div>` : 
                        '<div class="weather-good">Погода благоприятная</div>'}
                </div>
            `);
        
        // Добавляем номер точки маршрута
        marker.bindTooltip(`${index + 1}`, {
            permanent: true,
            direction: 'center',
            className: 'route-number'
        });
        
        markers.addLayer(marker);
        routePoints.push([location.coordinates.lat, location.coordinates.lon]);
    });
    
    // Добавляем маркеры на карту
    map.addLayer(markers);
    
    // Рисуем маршрут между точками
    if (routePoints.length > 1) {
        var routeLine = L.polyline(routePoints, {
            color: '#003366',
            weight: 3,
            opacity: 0.8,
            dashArray: '10, 10',
            animate: true
        }).addTo(map);
        
        // Добавляем стрелки направления маршрута
        var decorator = L.polylineDecorator(routeLine, {
            patterns: [
                {
                    offset: '5%',
                    repeat: '10%',
                    symbol: L.Symbol.arrowHead({
                        pixelSize: 10,
                        polygon: false,
                        pathOptions: {
                            color: '#003366',
                            fillOpacity: 1,
                            weight: 2
                        }
                    })
                }
            ]
        }).addTo(map);
    }
    
    // Подгоняем карту под все точки маршрута
    if (locations.length > 0) {
        map.fitBounds(markers.getBounds().pad(0.1));
    }
} 