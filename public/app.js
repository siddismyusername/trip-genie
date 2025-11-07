// TripGenie - Core Application Logic

const API_BASE = '/api';
const STORAGE_KEY = 'tripgenie_itinerary';
const DARK_MODE_KEY = 'tripgenie_dark_mode';

// API Client
const API = {
    async generateItinerary(preferences) {
        const response = await fetch(`${API_BASE}/generate-itinerary`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(preferences),
            signal: AbortSignal.timeout(120000) // 2 minutes timeout
        });
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to generate itinerary');
        }
        return response.json();
    },

    async getInterests() {
        const response = await fetch(`${API_BASE}/interests`);
        const data = await response.json();
        return data.interests || [];
    },

    async autocompleteLocation(query) {
        if (!query || query.length < 2) return [];
        const response = await fetch(`${API_BASE}/autocomplete-location?query=${encodeURIComponent(query)}`);
        const data = await response.json();
        return data.suggestions || [];
    },

    async validateLocation(location) {
        const response = await fetch(`${API_BASE}/validate-location`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ location })
        });
        return response.json();
    }
};

// Local Storage Helper
const Storage = {
    saveItinerary(itinerary) {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(itinerary));
    },
    
    getItinerary() {
        const data = localStorage.getItem(STORAGE_KEY);
        return data ? JSON.parse(data) : null;
    },
    
    clearItinerary() {
        localStorage.removeItem(STORAGE_KEY);
    },

    getDarkMode() {
        return localStorage.getItem(DARK_MODE_KEY) === 'true';
    },

    setDarkMode(enabled) {
        localStorage.setItem(DARK_MODE_KEY, enabled.toString());
    }
};

// Dark Mode Toggle
function initDarkMode() {
    const toggle = document.getElementById('darkModeToggle');
    if (!toggle) return;

    const isDark = Storage.getDarkMode();
    if (isDark) {
        document.documentElement.classList.add('dark');
    }

    toggle.addEventListener('click', () => {
        const isDark = document.documentElement.classList.toggle('dark');
        Storage.setDarkMode(isDark);
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    initDarkMode();
});

// Utility Functions
function formatDate(dateStr) {
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', { 
        weekday: 'short', 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
    });
}

function formatCurrency(amount, currency = 'USD') {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: currency
    }).format(amount);
}

function getWeatherClass(condition) {
    const c = condition.toLowerCase();
    if (c.includes('clear') || c.includes('sun')) return 'weather-clear';
    if (c.includes('rain')) return 'weather-rain';
    if (c.includes('snow')) return 'weather-snow';
    return 'weather-clouds';
}

function getWeatherEmoji(condition) {
    const c = condition.toLowerCase();
    if (c.includes('clear') || c.includes('sun')) return '☀️';
    if (c.includes('rain')) return '🌧️';
    if (c.includes('snow')) return '❄️';
    if (c.includes('cloud')) return '☁️';
    return '🌤️';
}
