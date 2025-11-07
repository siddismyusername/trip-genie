// Trip Planner Page Logic

let interests = [];
let debounceTimer;

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    init();
});

function setDefaultStartDate() {
    const startDateInput = document.getElementById('startDate');
    const today = new Date();
    const yyyy = today.getFullYear();
    const mm = String(today.getMonth() + 1).padStart(2, '0');
    const dd = String(today.getDate()).padStart(2, '0');
    startDateInput.value = `${yyyy}-${mm}-${dd}`;
}

// Initialize
function init() {
    const form = document.getElementById('tripForm');
    const destination = document.getElementById('destination');
    const startDate = document.getElementById('startDate');

    // Set default date to today
    setDefaultStartDate();

    // Autocomplete for destination
    let debounceTimer;
    destination?.addEventListener('input', (e) => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            showSuggestions(e.target.value);
        }, 300);
    });

    // Keyboard navigation for suggestions
    destination?.addEventListener('keydown', (e) => {
        const container = document.getElementById('suggestions');
        if (container.classList.contains('hidden')) return;
        const items = Array.from(container.querySelectorAll('.suggestion-item'));
        if (!items.length) return;

        const active = container.querySelector('.suggestion-active');
        let idx = active ? items.indexOf(active) : -1;

        if (e.key === 'ArrowDown') {
            e.preventDefault();
            if (idx < items.length - 1) idx++;
            else idx = 0;
            items.forEach(i=>i.classList.remove('suggestion-active'));
            items[idx].classList.add('suggestion-active');
            items[idx].scrollIntoView({ block: 'nearest' });
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            if (idx > 0) idx--;
            else idx = items.length - 1;
            items.forEach(i=>i.classList.remove('suggestion-active'));
            items[idx].classList.add('suggestion-active');
            items[idx].scrollIntoView({ block: 'nearest' });
        } else if (e.key === 'Enter') {
            if (idx >= 0) {
                e.preventDefault();
                items[idx].click();
            }
        } else if (e.key === 'Escape') {
            container.classList.add('hidden');
        }
    });

    // Click outside to close suggestions
    document.addEventListener('click', (e) => {
        if (!e.target.closest('#destination') && !e.target.closest('#suggestions')) {
            document.getElementById('suggestions')?.classList.add('hidden');
        }
    });

    // Interest button clicks
    document.querySelectorAll('.interest-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const interest = btn.dataset.interest;
            toggleInterest(interest, btn);
        });
    });

    // Form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        await handleSubmit();
    });

    renderInterests();
}

function toggleInterest(interest, button) {
    if (interests.includes(interest)) {
        // Remove interest
        interests = interests.filter(i => i !== interest);
        button.classList.remove('border-primary', 'text-white', 'bg-primary');
        button.classList.add('border-gray-300', 'dark:border-[#3b4c54]', 'text-gray-700', 'dark:text-gray-300', 'bg-white', 'dark:bg-transparent');
    } else {
        // Add interest
        interests.push(interest);
        button.classList.remove('border-gray-300', 'dark:border-[#3b4c54]', 'text-gray-700', 'dark:text-gray-300', 'bg-white', 'dark:bg-transparent');
        button.classList.add('border-primary', 'text-white', 'bg-primary');
    }
    renderInterests();
}

async function showSuggestions(query) {
    const container = document.getElementById('suggestions');
    
    if (!query || query.length < 2) {
        container.classList.add('hidden');
        return;
    }

    try {
        const suggestions = await API.autocompleteLocation(query);
        

        if (suggestions.length === 0) {
            container.classList.add('hidden');
            destination.setAttribute('aria-expanded', 'false');
            return;
        }

        // Dedupe and limit suggestions
        const seen = new Set();
        const deduped = [];
        for (const s of suggestions) {
            const key = (s.place_id || s.description || s.main_text || '').toString();
            if (!key) continue;
            if (seen.has(key)) continue;
            seen.add(key);
            deduped.push(s);
            if (deduped.length >= 6) break; // limit to 6
        }

        container.innerHTML = deduped.map((s, index) => `
            <div role="option" id="suggestion-${index}" tabindex="-1" class="suggestion-item text-gray-800 dark:text-white px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer" data-place="${s.description}">
                <div class="font-semibold">${s.main_text || s.description}</div>
                ${s.secondary_text ? `<div class="text-sm text-gray-500 dark:text-gray-400">${s.secondary_text}</div>` : ''}
            </div>
        `).join('');

    container.classList.remove('hidden');
    destination.setAttribute('aria-expanded', 'true');

        // Add click handlers
        container.querySelectorAll('.suggestion-item').forEach(item => {
            item.addEventListener('click', () => {
                document.getElementById('destination').value = item.dataset.place;
                container.classList.add('hidden');
                destination.focus();
                destination.setAttribute('aria-expanded', 'false');
            });
            // hover to set active for keyboard
            item.addEventListener('mouseenter', () => {
                container.querySelectorAll('.suggestion-item').forEach(i => i.classList.remove('suggestion-active'));
                item.classList.add('suggestion-active');
            });
        });
    } catch (error) {
        console.error('Autocomplete error:', error);
    }
}

function renderInterests() {
    const container = document.getElementById('interestTags');
    if (interests.length === 0) {
        container.innerHTML = '<p class="text-sm text-gray-500 dark:text-[#9cb0ba]">Select interests from the options below</p>';
        return;
    }
    
    container.innerHTML = interests.map(interest => `
        <span class="px-4 py-2 rounded-full border border-primary text-white bg-primary text-sm font-medium inline-flex items-center gap-2">
            ${interest}
            <button type="button" onclick="removeInterest('${interest}')" class="hover:text-red-200">×</button>
        </span>
    `).join('');
}

function removeInterest(interest) {
    interests = interests.filter(i => i !== interest);
    
    // Update button state
    document.querySelectorAll('.interest-btn').forEach(btn => {
        if (btn.dataset.interest === interest) {
            btn.classList.remove('border-primary', 'text-white', 'bg-primary');
            btn.classList.add('border-gray-300', 'dark:border-[#3b4c54]', 'text-gray-700', 'dark:text-gray-300', 'bg-white', 'dark:bg-transparent');
        }
    });
    renderInterests();
}

async function handleSubmit() {
    const generateBtn = document.getElementById('generateBtn');
    const loadingState = document.getElementById('loadingState');

    // Validate
    if (interests.length === 0) {
        alert('Please select at least one interest');
        return;
    }

    const destination = document.getElementById('destination').value;
    if (!destination) {
        alert('Please enter a destination');
        return;
    }

    // Show loading state
    generateBtn.disabled = true;
    loadingState.classList.remove('hidden');

    try {
        const preferences = {
            destination: document.getElementById('destination').value,
            origin: document.getElementById('origin').value || undefined,
            duration_days: parseInt(document.getElementById('duration').value),
            start_date: document.getElementById('startDate').value || undefined,
            budget: document.getElementById('budget').value,
            travel_style: document.getElementById('travelStyle').value,
            interests: interests
        };

        const result = await API.generateItinerary(preferences);

        if (result.success && result.itinerary) {
            Storage.saveItinerary(result.itinerary);
            window.location.href = 'itinerary.html';
        } else {
            throw new Error(result.error || 'Failed to generate itinerary');
        }
    } catch (error) {
        console.error('Error generating itinerary:', error);
        alert('Failed to generate itinerary. Please try again.');
    } finally {
        generateBtn.disabled = false;
        loadingState.classList.add('hidden');
    }
}

// Make functions globally accessible
window.removeInterest = removeInterest;
