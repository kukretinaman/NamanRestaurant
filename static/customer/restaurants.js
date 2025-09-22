document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('searchForm');
    const restaurantGrid = document.getElementById('restaurant-grid');
    const loading = document.getElementById('loading');
    const noResults = document.getElementById('no-results');
    
    // Load restaurants on page load
    loadRestaurants();
    
    // Handle search form submission
    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        loadRestaurants();
    });
    
    function loadRestaurants() {
        showLoading(true);
        
        const searchParams = new URLSearchParams();
        const search = document.getElementById('searchInput').value.trim();
        const location = document.getElementById('locationInput').value.trim();
        const cuisine = document.getElementById('cuisineSelect').value;
        
        if (search) searchParams.append('search', search);
        if (location) searchParams.append('location', location);
        if (cuisine) searchParams.append('cuisine', cuisine);
        
        const url = `/api/restaurants/?${searchParams.toString()}`;
        
        fetch(url)
            .then(response => response.json())
            .then(data => {
                showLoading(false);
                displayRestaurants(data);
            })
            .catch(error => {
                console.error('Error loading restaurants:', error);
                showLoading(false);
                showNoResults(true);
            });
    }
    
    function displayRestaurants(restaurants) {
        if (restaurants.length === 0) {
            showNoResults(true);
            return;
        }
        
        showNoResults(false);
        restaurantGrid.innerHTML = restaurants.map(restaurant => createRestaurantCard(restaurant)).join('');
    }
    
    function createRestaurantCard(restaurant) {
        return `
            <div class="restaurant-card">
                <div class="card-image">
                    ${restaurant.photo ? 
                        `<img src="${restaurant.photo}" alt="${restaurant.name}">` :
                        `<div class="placeholder-image">
                            <span class="placeholder-icon">🍴</span>
                            <span>No Image</span>
                        </div>`
                    }
                </div>
                
                <div class="card-content">
                    <div class="card-header">
                        <h3 class="restaurant-name">${restaurant.name}</h3>
                        ${restaurant.cuisine ? `<span class="cuisine-tag">${restaurant.cuisine}</span>` : ''}
                    </div>
                    
                    <div class="restaurant-info">
                        ${restaurant.address ? `<p class="address">${restaurant.address}</p>` : ''}
                    </div>
                    
                    <div class="card-actions">
                        <a href="/restaurant/${restaurant.id}/menu/" class="btn-primary">
                            View Menu
                        </a>
                        <button class="btn-secondary" onclick="toggleFavorite(${restaurant.id})">
                            ❤️ Favorite
                        </button>
                    </div>
                </div>
            </div>
        `;
    }
    
    function showLoading(show) {
        loading.style.display = show ? 'block' : 'none';
        restaurantGrid.style.display = show ? 'none' : 'grid';
    }
    
    function showNoResults(show) {
        noResults.style.display = show ? 'block' : 'none';
        restaurantGrid.style.display = show ? 'none' : 'grid';
    }
});

function toggleFavorite(restaurantId) {
    // Implement favorite functionality
    console.log('Toggle favorite for restaurant:', restaurantId);
}
