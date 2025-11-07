# Google Maps API Key Setup

To enable the interactive map on the itinerary page:

1. Get a Google Maps API Key:
   - Go to https://console.cloud.google.com/
   - Create a new project or select existing
   - Enable these APIs:
     - Maps JavaScript API
     - Places API (already enabled for autocomplete)
   - Create credentials → API Key
   - Restrict the key to your domain (or localhost for dev)

2. Add the API key to itinerary.html:
   - Open `public/itinerary.html`
   - Find line: `<script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&callback=initMap&libraries=places" async defer></script>`
   - Replace `YOUR_API_KEY` with your actual key

## Features Now Working:

- **Numbered markers** for each destination (1, 2, 3...)
- **Polyline route** connecting all locations in order
- **Info windows** showing place name and address on click
- **Auto-fit bounds** to show all destinations
- **Animated marker drops**

## Fallback:

If no API key is provided, the map will show a friendly message asking for the key.
