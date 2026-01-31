// static/js/main.js

// Configuración global
const API_BASE_URL = window.location.origin;

// Función para obtener CSRF token
function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}

// Función para hacer peticiones FETCH
async function fetchAPI(url, options = {}) {
    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCSRFToken()
        }
    };
    
    const mergedOptions = { ...defaultOptions, ...options };
    
    try {
        const response = await fetch(url, mergedOptions);
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error en petición:', error);
        throw error;
    }
}

// Función para mostrar notificaciones
function showNotification(message, type = 'info') {
    const container = document.querySelector('.container');
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
        <span>${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'}</span>
        ${message}
    `;
    
    container.insertBefore(alert, container.firstChild);
    
    // Auto-eliminar después de 5 segundos
    setTimeout(() => {
        alert.remove();
    }, 5000);
}

// Función para formatear moneda
function formatCurrency(value) {
    return new Intl.NumberFormat('es-BO', {
        style: 'currency',
        currency: 'BOB'
    }).format(value);
}

// Función para formatear fecha
function formatDate(date) {
    return new Date(date).toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

console.log('Main.js cargado correctamente');