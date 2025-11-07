// Itinerary Display Page Logic

let currentItinerary = null;
let map = null;
let markers = [];

// Global callback for Google Maps
window.initMap = function() {
    // Map will be initialized when itinerary is loaded
};

document.addEventListener('DOMContentLoaded', () => {
    loadItinerary();
    setupEventListeners();
});

function loadItinerary() {
    currentItinerary = Storage.getItinerary();
    
    if (!currentItinerary) {
        document.getElementById('noItinerary').classList.remove('hidden');
        document.getElementById('itineraryContent').classList.add('hidden');
        document.getElementById('actionButtons').classList.add('hidden');
        return;
    }

    document.getElementById('noItinerary').classList.add('hidden');
    document.getElementById('itineraryContent').classList.remove('hidden');
    document.getElementById('actionButtons').classList.remove('hidden');
    
    renderItinerary();
}

function renderItinerary() {
    if (!currentItinerary) return;

    // Title Section
    document.getElementById('destTitle').textContent = currentItinerary.destination;
    document.getElementById('dateRange').textContent = 
        `Your personalized itinerary for a memorable trip.`;
    
    // Trip Info Card
    document.getElementById('infoDestination').textContent = currentItinerary.destination;
    document.getElementById('infoDuration').textContent = 
        `${formatDate(currentItinerary.start_date)} - ${formatDate(currentItinerary.end_date).split(',')[0]}`;
    document.getElementById('infoBudget').textContent = currentItinerary.estimated_total_cost 
        ? formatCurrency(currentItinerary.estimated_total_cost)
        : 'Not specified';
    document.getElementById('infoStyle').textContent = 
        currentItinerary.travel_style ? currentItinerary.travel_style.charAt(0).toUpperCase() + currentItinerary.travel_style.slice(1) : 'Moderate';

    // Render days and destinations
    renderDays();
    renderDestinationList();
    renderMap();
}

function renderDays() {
    const container = document.getElementById('daysContainer');
    
    container.innerHTML = currentItinerary.days.map((day, index) => `
        <details class="group bg-white dark:bg-[#1a2831] rounded-xl border border-slate-200 dark:border-[#3b4c54] open:border-primary transition-colors" ${index === 0 ? 'open' : ''}>
            <summary class="list-none flex justify-between items-center p-4 cursor-pointer">
                <div class="flex flex-col">
                    <h3 class="text-lg font-bold text-slate-900 dark:text-white">Day ${day.day_number}: ${day.activities[0]?.place.name || `Day ${day.day_number}`}</h3>
                    <p class="text-sm text-slate-500 dark:text-slate-400">${formatDate(day.date)}</p>
                </div>
                <div class="flex items-center gap-4">
                    ${day.weather ? `
                        <div class="flex items-center gap-2 rounded-full bg-slate-100 dark:bg-[#283339] px-3 py-1 text-sm text-slate-700 dark:text-slate-300">
                            <span class="material-symbols-outlined text-base ${getWeatherColor(day.weather.condition)}">${getWeatherIcon(day.weather.condition)}</span>
                            <span>${Math.round(day.weather.temperature_max)}°C</span>
                        </div>
                    ` : ''}
                    <span class="material-symbols-outlined transition-transform duration-300 group-open:rotate-180">expand_more</span>
                </div>
            </summary>
            <div class="px-4 pb-4 flex flex-col gap-3">
                ${day.activities.map(activity => `
                    <div class="flex items-start gap-4 p-3 rounded-lg bg-slate-50 dark:bg-[#101c22]">
                        <div class="bg-primary/20 text-primary p-2 rounded-full">
                            <span class="material-symbols-outlined">${getActivityIcon(activity.activity_type)}</span>
                        </div>
                        <div class="flex-1">
                            <p class="font-bold text-slate-900 dark:text-white">${activity.time}: ${activity.place.name}</p>
                            <p class="text-sm text-slate-600 dark:text-slate-400">${activity.notes || activity.activity_type}</p>
                            ${activity.estimated_cost ? `<p class="text-sm text-primary font-semibold mt-1">${formatCurrency(activity.estimated_cost)}</p>` : ''}
                        </div>
                    </div>
                `).join('')}
            </div>
        </details>
    `).join('');
}

function getWeatherIcon(condition) {
    if (!condition) return 'wb_sunny';
    const c = condition.toLowerCase();
    if (c.includes('rain') || c.includes('shower')) return 'rainy';
    if (c.includes('cloud')) return 'cloudy';
    if (c.includes('sun') || c.includes('clear')) return 'sunny';
    if (c.includes('snow')) return 'ac_unit';
    return 'wb_sunny';
}

function getWeatherColor(condition) {
    if (!condition) return 'text-yellow-500';
    const c = condition.toLowerCase();
    if (c.includes('rain')) return 'text-blue-500';
    if (c.includes('cloud')) return 'text-cyan-400';
    if (c.includes('sun') || c.includes('clear')) return 'text-yellow-500';
    return 'text-slate-400';
}

function getActivityIcon(type) {
    if (!type) return 'place';
    const t = type.toLowerCase();
    if (t.includes('food') || t.includes('restaurant') || t.includes('dining')) return 'restaurant';
    if (t.includes('museum') || t.includes('gallery')) return 'museum';
    if (t.includes('park') || t.includes('garden')) return 'park';
    if (t.includes('shop')) return 'shopping_bag';
    if (t.includes('hotel') || t.includes('accommodation')) return 'hotel';
    if (t.includes('transport') || t.includes('travel')) return 'directions_car';
    if (t.includes('tour') || t.includes('sightseeing')) return 'tour';
    if (t.includes('art') || t.includes('culture')) return 'palette';
    if (t.includes('entertainment') || t.includes('show')) return 'theater_comedy';
    if (t.includes('beach')) return 'beach_access';
    if (t.includes('flight') || t.includes('airport')) return 'flight_land';
    if (t.includes('cruise') || t.includes('boat')) return 'directions_boat';
    return 'place';
}

function renderMap() {
    // Check if Google Maps is loaded
    if (typeof google === 'undefined' || !google.maps) {
        document.getElementById('map').innerHTML = 
            '<div class="flex items-center justify-center h-full text-gray-500 dark:text-gray-400">Google Maps API not loaded. Please add your API key.</div>';
        return;
    }

    // Collect all locations
    const locations = [];
    currentItinerary.days.forEach(day => {
        day.activities.forEach(activity => {
            locations.push({
                name: activity.place.name,
                lat: activity.place.location.latitude,
                lng: activity.place.location.longitude,
                address: activity.place.location.address
            });
        });
    });

    if (locations.length === 0) {
        document.getElementById('map').innerHTML = 
            '<div class="flex items-center justify-center h-full text-gray-500 dark:text-gray-400">No locations to display</div>';
        return;
    }

    // Initialize map centered on first location
    const mapElement = document.getElementById('map');
    map = new google.maps.Map(mapElement, {
        zoom: 12,
        center: { lat: locations[0].lat, lng: locations[0].lng },
        mapTypeControl: true,
        streetViewControl: false,
        fullscreenControl: true,
        styles: [
            {
                featureType: "poi",
                elementType: "labels",
                stylers: [{ visibility: "off" }]
            }
        ]
    });

    // Add markers for each location with custom styling
    const bounds = new google.maps.LatLngBounds();
    locations.forEach((location, index) => {
        const marker = new google.maps.Marker({
            position: { lat: location.lat, lng: location.lng },
            map: map,
            title: location.name,
            label: {
                text: (index + 1).toString(),
                color: '#ffffff',
                fontSize: '14px',
                fontWeight: 'bold'
            },
            icon: {
                path: google.maps.SymbolPath.CIRCLE,
                scale: 20,
                fillColor: '#0da6f2',
                fillOpacity: 1,
                strokeColor: '#ffffff',
                strokeWeight: 3
            },
            animation: google.maps.Animation.DROP
        });

        // Info window with better styling
        const infoWindow = new google.maps.InfoWindow({
            content: `
                <div style="padding: 8px; min-width: 200px;">
                    <div style="color: #0da6f2; font-weight: bold; font-size: 14px; margin-bottom: 4px;">
                        ${index + 1}. ${location.name}
                    </div>
                    <div style="color: #666; font-size: 12px;">${location.address || 'Address not available'}</div>
                </div>
            `
        });

        marker.addListener('click', () => {
            // Close all other info windows
            markers.forEach(m => {
                if (m.infoWindow) m.infoWindow.close();
            });
            infoWindow.open(map, marker);
        });

        marker.infoWindow = infoWindow;
        markers.push(marker);
        bounds.extend(marker.getPosition());
    });

    // Fit map to show all markers
    if (locations.length > 1) {
        map.fitBounds(bounds);
    } else {
        map.setZoom(14);
    }

    // Draw polyline connecting locations sequentially
    if (locations.length > 1) {
        const path = locations.map(loc => ({ lat: loc.lat, lng: loc.lng }));
        const polyline = new google.maps.Polyline({
            path: path,
            geodesic: true,
            strokeColor: '#0da6f2',
            strokeOpacity: 0.8,
            strokeWeight: 4
        });
        polyline.setMap(map);
    }
}

function renderDestinationList() {
    const container = document.getElementById('destinationList');
    const destinations = [];
    
    currentItinerary.days.forEach(day => {
        day.activities.forEach((activity, actIndex) => {
            destinations.push({
                name: activity.place.name,
                day: day.day_number,
                lat: activity.place.location.latitude,
                lng: activity.place.location.longitude
            });
        });
    });

    container.innerHTML = destinations.map((dest, index) => `
        <div class="flex items-center gap-3 group cursor-pointer hover:bg-slate-50 dark:hover:bg-[#101c22] p-2 rounded-lg transition-colors" onclick="focusOnPlace(${dest.lat}, ${dest.lng}, '${dest.name}')">
            <span class="material-symbols-outlined text-slate-400 dark:text-slate-500 group-hover:text-slate-600 dark:group-hover:text-slate-300">drag_indicator</span>
            <div class="flex-1">
                <p class="font-medium text-slate-800 dark:text-slate-200">${dest.name}</p>
                <p class="text-sm text-slate-500 dark:text-slate-400">Day ${dest.day}</p>
            </div>
            <div class="size-8 rounded-full bg-primary flex items-center justify-center text-white font-bold text-sm">${index + 1}</div>
        </div>
    `).join('');

    // Make destination list sortable
    if (typeof Sortable !== 'undefined') {
        new Sortable(container, {
            animation: 150,
            handle: '.material-symbols-outlined',
            ghostClass: 'opacity-50'
        });
    }
}

function focusOnPlace(lat, lng, name) {
    if (!map) return;
    
    map.panTo({ lat, lng });
    map.setZoom(15);
    
    // Find and open the marker's info window
    markers.forEach(marker => {
        if (marker.getTitle() === name) {
            google.maps.event.trigger(marker, 'click');
        }
    });
}

function setupEventListeners() {
    // Close day details panel
    document.getElementById('closeDayDetails')?.addEventListener('click', () => {
        document.getElementById('dayDetailsPanel').classList.add('hidden');
    });

    // Export JSON
    document.getElementById('exportJSON')?.addEventListener('click', () => {
        const dataStr = JSON.stringify(currentItinerary, null, 2);
        const blob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `itinerary-${currentItinerary.destination.replace(/\s+/g, '-')}.json`;
        a.click();
        URL.revokeObjectURL(url);
    });

    // Export PDF
    document.getElementById('exportPDF')?.addEventListener('click', () => {
        if (typeof jspdf === 'undefined') {
            alert('PDF library not loaded');
            return;
        }
        
        const { jsPDF } = window.jspdf;
        const doc = new jsPDF();
        
        doc.setFontSize(20);
        doc.text(`TripGenie Itinerary`, 20, 20);
        doc.setFontSize(16);
        doc.text(currentItinerary.destination, 20, 30);
        doc.setFontSize(12);
        doc.text(`${currentItinerary.start_date} to ${currentItinerary.end_date}`, 20, 38);
        
        let y = 50;
        currentItinerary.days.forEach(day => {
            if (y > 270) {
                doc.addPage();
                y = 20;
            }
            doc.setFontSize(14);
            doc.text(`Day ${day.day_number} - ${day.date}`, 20, y);
            y += 8;
            
            day.activities.forEach(activity => {
                if (y > 270) {
                    doc.addPage();
                    y = 20;
                }
                doc.setFontSize(10);
                doc.text(`${activity.time} - ${activity.place.name}`, 25, y);
                y += 6;
            });
            y += 5;
        });
        
        doc.save(`itinerary-${currentItinerary.destination.replace(/\s+/g, '-')}.pdf`);
    });

    // New Trip
    document.getElementById('newTrip')?.addEventListener('click', () => {
        if (confirm('Start a new trip? This will clear your current itinerary.')) {
            Storage.clearItinerary();
            window.location.href = 'planner.html';
        }
    });

    // Add Destination (placeholder)
    document.getElementById('addDestination')?.addEventListener('click', () => {
        alert('Add Destination feature coming soon!');
    });

    // Export Plan (alternative export)
    document.getElementById('exportPlan')?.addEventListener('click', () => {
        const menu = document.createElement('div');
        menu.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        menu.innerHTML = `
            <div class="bg-white dark:bg-gray-800 rounded-xl p-6 max-w-sm w-full mx-4">
                <h3 class="text-xl font-bold mb-4 text-gray-800 dark:text-white">Export Your Plan</h3>
                <div class="space-y-2">
                    <button class="w-full px-4 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition" onclick="document.getElementById('exportJSON').click(); this.closest('.fixed').remove();">
                        📄 Export as JSON
                    </button>
                    <button class="w-full px-4 py-3 bg-secondary text-white rounded-lg hover:bg-cyan-600 transition" onclick="document.getElementById('exportPDF').click(); this.closest('.fixed').remove();">
                        📑 Export as PDF
                    </button>
                    <button class="w-full px-4 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 transition" onclick="this.closest('.fixed').remove();">
                        Cancel
                    </button>
                </div>
            </div>
        `;
        document.body.appendChild(menu);
    });
}

// Make functions globally accessible
window.showDayDetails = showDayDetails;
window.focusOnPlace = focusOnPlace;
