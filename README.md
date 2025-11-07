# TripGenie
AI-powered itinerary generator using a modular multi-agent design.

This repository contains TripGenie: a small multi-agent system that composes real-time data (Google Maps / Places, weather) with LLM reasoning (via Ollama / Llama 3) to produce day-by-day travel itineraries.

This README is a compact developer quick-start. More detailed design and agent docs live in `agent/README.md` and `agent/architecture.md`.

## Quick start (development, Windows)

Prerequisites
- Python 3.11+
- Node.js + npm (for the simple Node gateway)
- Google Cloud API key (Places / Geocoding enabled)
- Optional: OpenWeather API key (the project falls back to wttr.in if absent)
- Ollama running with a Llama 3 model for local LLM calls (recommended)

Steps

1. Copy environment template and add keys

```cmd
cd s:\project\TripGen\trip-genie\agent
copy .env.example .env
rem edit agent\.env and add your GOOGLE_MAPS_API_KEY, OPENWEATHER_API_KEY, OLLAMA_BASE_URL, OLLAMA_MODEL
```

2. Activate Python virtualenv (this repo ships a venv under `agent/env`)

```cmd
agent\env\Scripts\activate.bat
pip install -r agent\requirements.txt
```

3. Start Ollama (if using Llama 3)

Follow Ollama instructions: https://ollama.ai — ensure the model named in `agent/.env` is pulled and `ollama serve` is running.

4. Start the app (node gateway + python backend)

```cmd
cd s:\project\TripGen\trip-genie
npm run dev
```

This runs the Python FastAPI backend and the Node gateway concurrently. The gateway serves the frontend in `public/` and proxies API calls to the Python backend.

## Developer notes — important files

- `agent/` — core implementation of the multi-agent workflow
	- `agent/base_agent.py` — base classes (BaseAgent, LLMAgent) and the `SequentialAgent` orchestrator
	- `agent/agents.py` — concrete agents (InputValidatorAgent, RouteExplorerAgent, DistanceEvaluatorAgent, WeatherOptimizerAgent, PlaceRankerAgent, ItineraryPlannerAgent, etc.)
	- `agent/workflow.py` — `TripGenieWorkflow` that composes agents; the convenience function `generate_trip_itinerary` is here
	- `agent/models.py` — Pydantic models defining AgentInput / AgentOutput and domain models (Place, Location, Itinerary)
	- `agent/utils.py` — integration helpers (geocoding, places, weather, distance calculations)
	- `agent/config.py` — settings loader (reads `agent/.env` and repo `.env`)

- `public/` — static frontend (planner, itinerary viewer, asset files)
	- `public/planner.html`, `public/planner.js` — trip creation UI and autocomplete logic
	- `public/itinerary.html`, `public/itinerary.js` — itinerary viewer and map rendering

- `server.js` — lightweight Node gateway that proxies requests to the Python backend and serves `public/`
- `agent/server.py` — FastAPI backend that exposes endpoints such as `/api/generate-itinerary`, `/api/autocomplete-location`, `/api/validate-location`.

## How the system works (high level)

1. Frontend collects user preferences and calls the Node gateway (`/api/generate-itinerary`).
2. Gateway proxies to the Python FastAPI backend.
3. The backend runs `TripGenieWorkflow`, which calls agents in sequence:
	 - InputValidatorAgent: validates prefs and geocodes origin/destination
	 - RouteExplorerAgent: fetches places via Google Places (textsearch)
	 - DistanceEvaluatorAgent: filters/prioritizes places by distance
	 - WeatherOptimizerAgent: fetches weather (heuristic Google scrape then `wttr.in` fallback)
	 - PlaceRankerAgent: calls LLM (Ollama) to score places
	 - ItineraryPlannerAgent: uses LLM to create a structured day-by-day itinerary
	 - CostEstimatorAgent: estimates costs

Agents exchange simple JSON-like data (dicts). When adding or changing fields, update `agent/models.py` to keep schemas consistent.

## API endpoints (examples)

- Health: GET `/health` — checks backend config and LLM availability
- Generate itinerary: POST `/api/generate-itinerary` — request body follows `agent/models.UserPreferences`
- Autocomplete: GET `/api/autocomplete-location?query=...` — returns structured suggestions
- Validate location: POST `/api/validate-location` — returns geocoded location

## Notes & troubleshooting

- `agent/config.py` loads `agent/.env` first to make local development convenient. If you prefer a different setup, move your `.env` to the repo root or update the loader.
- The app expects a working Google Maps / Places API key. If you see `Google Maps API key not configured` in logs, double-check `agent/.env` contains `GOOGLE_MAPS_API_KEY` and that the Pydantic settings picked it up (see `/health` endpoint).
- Weather fetching uses a lightweight heuristic scrape of Google Search and falls back to `wttr.in` if unavailable. This is intentional to avoid requiring paid weather APIs.
- LLM calls use Ollama (`agent/base_agent.py::LLMAgent.call_llm`). Make sure Ollama is running and the model name in the env is correct.

## Contributing / extending

- To add a new agent, implement a class in `agent/agents.py` inheriting from `BaseAgent` or `LLMAgent`, update the `TripGenieWorkflow` agent list in `agent/workflow.py`, and add/adjust Pydantic models in `agent/models.py`.
- Keep LLM prompts and parsing defensive; `PlaceRankerAgent` demonstrates defensive JSON extraction with a rating-based fallback.

## Where to look next
- `agent/README.md` — more detailed developer guide and examples (agent testing notebook `agent-development.ipynb`)
- `agent/architecture.md` — design rationale and sequence diagrams

If you want, I can expand this README with a short troubleshooting section for common console errors (Google Maps referer restrictions, Ollama connection errors, missing API keys). Tell me which area to expand.

