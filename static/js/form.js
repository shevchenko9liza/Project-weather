document.getElementById('add-location').addEventListener('click', function() {
    const container = document.getElementById('locations-container');
    const newLocation = document.createElement('div');
    newLocation.className = 'location-input';
    newLocation.innerHTML = `
        <label>Промежуточная точка:</label>
        <input type="text" name="locations[]" required>
        <button type="button" class="remove-location">Удалить</button>
    `;
    container.appendChild(newLocation);
});

document.addEventListener('click', function(e) {
    if (e.target.classList.contains('remove-location')) {
        e.target.parentElement.remove();
    }
}); 