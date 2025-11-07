# TripGenie ADK + Llama 3 Architecture Document

## 1. Project Overview

**Project Name:** TripGenie – AI-Powered Itinerary Planner
**Objective:** Build an intelligent, modular itinerary planning system using **Google's Agent Development Kit (ADK)** for orchestration and **Llama 3** for reasoning, powered by real-time APIs (Google Maps + Weather).

The goal is to create a highly modular, anti-hallucination AI workflow that generates personalized travel itineraries based on validated data and user preferences.

---

## 2. System Architecture Overview

TripGenie will follow a **multi-agent sequential architecture** orchestrated by Google ADK. Each agent performs a distinct sub-task, ensuring accuracy, modularity, and reliability.

### High-Level Flow

```
User → Frontend (HTML + Tailwind)
        ↓
Backend Orchestrator (Express.js)
        ↓
Google ADK Agent Orchestration Layer
        ↓
Llama 3 (via Ollama / Vertex AI / Hugging Face)
        ↓
External APIs (Maps, Weather)
        ↓
Frontend (rendered itinerary)
```

---

## 3. Agent Orchestration Layer (ADK)

### 3.1 Agents Overview

The orchestration layer is composed of the following micro-agents, each mapped to a clearly defined function.

| Agent                         | Type                   | Description                                                                         |
| ----------------------------- | ---------------------- | ----------------------------------------------------------------------------------- |
| **InputValidator Agent**      | Deterministic          | Validates and normalizes user inputs. Fetches geolocation data via Google Maps API. |
| **RouteExplorer Agent**       | API-driven             | Finds en-route or nearby tourist attractions using Maps Places API.                 |
| **DistanceEvaluator Agent**   | Computational          | Calculates distances between locations and prunes outliers.                         |
| **WeatherOptimizer Agent**    | API-driven             | Adjusts itinerary days based on real-time weather forecasts.                        |
| **PlaceRanker Agent**         | LLM-assisted (Llama 3) | Scores and ranks places by popularity and user interest match.                      |
| **ItineraryPlanner Agent**    | LLM-driven (Llama 3)   | Generates day-wise itinerary in structured JSON format.                             |
| **PreferenceValidator Agent** | Rule-based             | Validates itinerary balance between journey vs. destination focus.                  |
| **OutputFormatter Agent**     | Deterministic          | Converts itinerary JSON into a frontend-renderable HTML/PDF structure.              |

---

### 3.2 Agent Chaining

Each agent passes validated data to the next step. Google ADK's **SequentialAgent** structure handles the chaining.

```python
from google.adk import SequentialAgent

tripgenie_workflow = SequentialAgent(
    agents=[
        InputValidator(),
        RouteExplorer(),
        DistanceEvaluator(),
        WeatherOptimizer(),
        PlaceRanker(model=llama3),
        ItineraryPlanner(model=llama3),
        PreferenceValidator(),
        OutputFormatter()
    ]
)
```

ADK ensures schema validation and automatic retry if any step fails or produces malformed data.

---

## 4. Backend Layer

**Technology:** Express.js (Node.js)

### Responsibilities:

* Acts as the central API gateway.
* Receives user input from frontend.
* Sends structured requests to the ADK workflow.
* Handles API key security (Maps, Weather).
* Returns AI-validated itinerary to frontend.

### Sample Express Endpoint

```javascript
app.post('/api/generate-itinerary', async (req, res) => {
  const userPrefs = req.body;
  const result = await tripgenie_workflow.run(userPrefs);
  res.json(result);
});
```

---

## 5. Frontend Layer

**Technology:** HTML + Tailwind CSS

### Features:

* Form for user input: destination, duration, interests, budget, travel style.
* Responsive, modern UI with progress loader during AI generation.
* Renders itinerary cards grouped by day, weather, and activity type.

---

## 6. Integration with External APIs

| API                                   | Usage                                           | Integration Method   |
| ------------------------------------- | ----------------------------------------------- | -------------------- |
| **Google Maps API**                   | Fetch locations, distances, coordinates         | REST API via API key |
| **OpenWeather API**                   | Fetch 5-day forecast for itinerary optimization | REST API via API key |
| **Hugging Face / Ollama / Vertex AI** | Run Llama 3 inference                           | Model endpoint       |

---

## 7. Anti-Hallucination Strategy

| Level        | Technique                                                              |
| ------------ | ---------------------------------------------------------------------- |
| Input        | Strict JSON schema validation via ADK                                  |
| Data         | Real-time data retrieval from APIs                                     |
| Reasoning    | Llama 3 only used for ranking and text structuring, not fact retrieval |
| Output       | JSON schema + ADK re-prompting if violated                             |
| Post-process | Rule-based verification in PreferenceValidator Agent                   |

This ensures the system outputs only validated, factual, reproducible itineraries.

---

**End of Document**
