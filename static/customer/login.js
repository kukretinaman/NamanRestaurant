document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const errorMessage = document.getElementById('error-message');
    
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
        setTimeout(() => {
            errorMessage.style.display = 'none';
        }, 5000);
    }

    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const username = document.getElementById('emailInput').value.trim();
        const password = document.getElementById('passwordInput').value.trim();
        
        if (!username || !password) {
            showError('Please enter both username and password');
            return;
        }
        
        // For now, use Django's regular login (can be upgraded to JWT later)
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);
        formData.append('csrfmiddlewaretoken', getCookie('csrftoken'));
        
        fetch(window.location.href, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            }
        })
        .then(response => {
            if (response.redirected) {
                window.location.href = response.url;
            } else {
                return response.text();
            }
        })
        .then(html => {
            if (html) {
                if (html.includes('error') || html.includes('invalid')) {
                    showError('Invalid username or password');
                } else {
                    window.location.href = '/restaurants/';
                }
            }
        })
        .catch(error => {
            console.error('Login error:', error);
            showError('Login failed. Please try again.');
        });
    });
    
    // Get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
