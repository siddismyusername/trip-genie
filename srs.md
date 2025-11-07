# TripGenie SRS – Updated with Agent Architecture, UI Requirements, and Functional Enhancements

---

## **1. Introduction**

### **1.1 Purpose**

This document defines the software requirements for **TripGenie: AI-Powered Itinerary Planner**, an intelligent, modular travel-planning system using **Google’s Agent Development Kit (ADK)** and **Llama 3** for reasoning. It includes both **UI Requirements** and **functional updates**, reflecting the shift to a React-based frontend and improved user input features.

### **1.2 Scope**

TripGenie is a web-based application that generates personalized itineraries based on user preferences and real-time data (maps and weather). It uses modular AI agents for reasoning and data validation, ensuring accuracy and minimizing hallucination.

**Key Components:**

* Frontend: React (with Material UI)
* Backend: Node.js + Express.js
* AI Orchestration: Google ADK
* LLM: Llama 3 (via Ollama, Vertex AI, or Hugging Face)
* APIs: Google Maps, OpenWeather

---

## **2. System Overview**

TripGenie operates on a **multi-agent sequential architecture** orchestrated through Google ADK. Each agent performs an independent subtask, passing validated data to the next. The modular design enhances explainability, debugging, and future scalability.

**System Flow:**

```
User → Frontend (React + Material UI)
        ↓
Backend (Node.js + Express.js)
        ↓
ADK Orchestrator
        ↓
Llama 3 (Reasoning)
        ↓
External APIs (Maps, Weather)
        ↓
Frontend (Rendered Itinerary)
```

---

## **3. Functional Requirements**

### **3.1 Agents Overview**

| Agent                     | Type                   | Description                                                              |
| ------------------------- | ---------------------- | ------------------------------------------------------------------------ |
| InputValidator Agent      | Deterministic          | Validates and normalizes user input, ensures data completeness.          |
| RouteExplorer Agent       | API-driven             | Fetches tourist attractions and travel routes using Google Maps API.     |
| DistanceEvaluator Agent   | Computational          | Filters results by travel distance, ensures efficiency.                  |
| WeatherOptimizer Agent    | API-driven             | Integrates weather data to reorder or replace outdoor/indoor activities. |
| PlaceRanker Agent         | LLM-assisted (Llama 3) | Scores and ranks places based on user interests and ratings.             |
| ItineraryPlanner Agent    | LLM-driven (Llama 3)   | Generates structured day-wise itineraries.                               |
| PreferenceValidator Agent | Rule-based             | Checks itinerary alignment with user’s travel focus preferences.         |
| OutputFormatter Agent     | Deterministic          | Converts JSON output into a readable format for frontend.                |

---

### **3.2 Frontend Functional Requirements**

| ID   | Feature                                             | Description                                                                                                     |
| ---- | --------------------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| FR-1 | **Trip Input Form**                                 | Collect user preferences such as destination, dates, budget, and interests.                                     |
| FR-2 | **AI Processing Trigger**                           | On clicking “Generate Itinerary,” send structured JSON to backend for AI processing.                            |
| FR-3 | **Real-Time Autocorrect & Suggestion for Location** | Use Google Places Autocomplete API to suggest and autocorrect destinations as users type in the location field. |
| FR-4 | **Input Validation**                                | Prevent submission until required fields are completed.                                                         |
| FR-5 | **Error Handling**                                  | Show error alerts when APIs or LLMs fail.                                                                       |
| FR-6 | **Persistent State**                                | Store last itinerary using localStorage or sessionStorage.                                                      |
| FR-7 | **Export Options**                                  | Allow users to download or share itineraries as PDF or JSON.                                                    |
| FR-8 | **Dark Mode Toggle**                                | Support a dark/light theme switch for accessibility.                                                            |

---

## **4. UI Requirements – TripGenie: AI-Powered Itinerary Planner**

### **4.1 Overview**

The UI acts as the interaction layer between users and the AI system. It should feel modern, elegant, and highly interactive. Built with **React and Material UI**, it ensures modular component-based rendering and real-time reactivity.

**Frontend Stack:**

* React.js (component-driven architecture)
* Material UI (for design and styling)
* JavaScript / TypeScript (for logic)

### **4.2 Design Objectives**

* Clean, modular, and responsive design.
* Real-time interaction using React hooks and state.
* Visual feedback for loading and validation.
* Material Design 3 compliance for accessibility and clarity.

---

### **4.3 UI Components**

#### **Landing Page**

| ID     | Description                                              |
| ------ | -------------------------------------------------------- |
| UI-1.1 | Display title “TripGenie: AI Itinerary Planner.”         |
| UI-1.2 | Subtitle: “Plan your perfect trip in seconds using AI.”  |
| UI-1.3 | “Start Planning” CTA leading to form page.               |
| UI-1.4 | Background with dynamic gradient or travel illustration. |
| UI-1.5 | Optimized layout for all screen sizes.                   |

#### **Trip Input Form**

| ID     | Description                                                                                      |
| ------ | ------------------------------------------------------------------------------------------------ |
| UI-2.1 | Collect destination, start/end dates, budget, interests, and preferences.                        |
| UI-2.2 | **Google Places Autocomplete** for destination input with real-time suggestions and autocorrect. |
| UI-2.3 | Dropdowns for travel type, intensity, and accommodation.                                         |
| UI-2.4 | Tooltips and placeholders for guidance.                                                          |
| UI-2.5 | Submit button disabled until validation passes.                                                  |
| UI-2.6 | Circular progress indicator during AI computation.                                               |

#### **Itinerary Display Page**

| ID      | Description                                                                                                                    |
| ------- | ------------------------------------------------------------------------------------------------------------------------------ |
| UI-3.1  | Summary card: destination, duration, and budget.                                                                               |
| UI-3.2  | Expandable cards per day using Material UI Accordions.                                                                         |
| UI-3.3  | Include weather badges per day.                                                                                                |
| UI-3.4  | Visual icons for activity types.                                                                                               |
| UI-3.5  | Option to re-generate or edit preferences.                                                                                     |
| UI-3.6  | Export as PDF/JSON.                                                                                                            |
| UI-3.7  | **Interactive Map Integration:** Display a Google Map showing all destinations marked with pins.                               |
| UI-3.8  | **Editable Destination List:** Show a draggable, editable list of destinations in sequence. Users can reorder or rename items. |
| UI-3.9  | **Add Destination Button:** Allow users to add new destinations using a Google Places Autocomplete search box.                 |
| UI-3.10 | **Export Plan Button:** Export the updated itinerary (with custom destinations) as PDF or JSON.                                |

---

### **4.4 Accessibility and Responsiveness**

| ID     | Requirement                                                       |
| ------ | ----------------------------------------------------------------- |
| UI-5.1 | Ensure keyboard accessibility and ARIA support.                   |
| UI-5.2 | Adjust layouts dynamically across breakpoints (Material UI Grid). |
| UI-5.3 | Support light/dark themes with smooth transitions.                |
| UI-5.4 | Use high-contrast color pairs for text readability.               |

---

## **5. User Preferences Schema**

```json
{
  "user_preferences": {
    "destination": "Kyoto, Japan",
    "trip_duration": 4,
    "start_date": "2025-03-20",
    "number_of_travelers": 2,
    "budget_type": "Moderate",
    "accommodation_type": "Hotel",
    "transport_mode": "Public Transport",
    "meal_preference": "Veg",
    "interests": ["Culture", "Nature", "Food"],
    "activity_intensity": "Balanced",
    "special_interests": "Tea ceremonies and cherry blossom viewing",
    "weather_preference": "Avoid Rain",
    "distance_preference": "Short Distances",
    "time_preference": "Morning Person",
    "local_experience_level": "First-time",
    "output_format": "JSON",
    "include_cost_estimate": true,
    "include_weather_forecast": true
  },
  "external_data": {
    "weather_forecast": "...",
    "places_data": "...",
    "maps_distance_matrix": "..."
  }
}
```

---

## **6. Non-Functional Requirements**

| Requirement     | Description                                        |
| --------------- | -------------------------------------------------- |
| Performance     | Itinerary generation under 15 seconds.             |
| Scalability     | Concurrent user support through ADK orchestration. |
| Reliability     | Schema validation ensures consistency.             |
| Security        | No storage of sensitive user data.                 |
| Maintainability | Modular agent and component design.                |
| Usability       | Intuitive React UI, keyboard navigation support.   |

---

**End of Updated SRS Document**