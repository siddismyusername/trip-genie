# TripGenie - AI-Powered Itinerary Planner

An intelligent, modular itinerary planning system using **Agent Development Kit (ADK)** architecture and **Llama 3** for reasoning, powered by real-time APIs (Google Maps + Weather).

## 🌟 Features

- **Multi-Agent Architecture**: Sequential agent orchestration for reliable, modular processing
- **Anti-Hallucination Design**: Real-time data validation and fact-based reasoning
- **LLM-Powered Ranking**: Llama 3 integration for intelligent place recommendations
- **Weather-Aware Planning**: Optimizes itineraries based on weather forecasts
- **RESTful API**: FastAPI backend with comprehensive endpoints
- **Fully Typed**: Pydantic models for data validation and type safety

## 🏗️ Architecture

TripGenie follows a **multi-agent sequential architecture** with specialized agents:

```
User Input
    ↓
InputValidatorAgent → RouteExplorerAgent → DistanceEvaluatorAgent
    ↓
WeatherOptimizerAgent → PlaceRankerAgent → ItineraryPlannerAgent
    ↓
Complete Itinerary
```

### Agent Breakdown

| Agent | Type | Purpose |
|-------|------|---------|
| **InputValidator** | Deterministic | Validates inputs & geocodes locations |
| **RouteExplorer** | API-driven | Finds tourist attractions via Google Maps |
| **DistanceEvaluator** | Computational | Calculates distances & filters outliers |
| **WeatherOptimizer** | API-driven | Fetches weather forecasts |
| **PlaceRanker** | LLM-assisted | Ranks places using Llama 3 |
| **ItineraryPlanner** | LLM-driven | Generates structured day-wise itinerary |

## 📦 Installation

### Prerequisites

- Python 3.11+
- Google Maps API key
- OpenWeather API key
- Ollama with Llama 3 model

### Setup

1. **Clone the repository**
```bash
cd s:\project\TripGen\trip-geni\agent
```

2. **Create virtual environment** (already exists in your case)
```bash
python -m venv env
env\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
copy .env.example .env
```

Edit `.env` and add your API keys:
```env
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here
OPENWEATHER_API_KEY=your_openweather_api_key_here
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```

5. **Install and run Ollama**
```bash
# Download Ollama from https://ollama.ai
ollama pull llama3
ollama serve
```

## 🚀 Usage

### Option 1: Python API

```python
from workflow import generate_trip_itinerary
import asyncio

async def main():
    result = await generate_trip_itinerary(
        destination="Paris, France",
        duration_days=5,
        interests=["culture", "art", "food", "history"],
        budget="medium",
        travel_style="moderate",
        start_date="2025-12-01"
    )
    
    if result["success"]:
        print(result["itinerary"])
    else:
        print(f"Error: {result['error']}")

asyncio.run(main())
```

### Option 2: REST API Server

Start the server:
```bash
python server.py
```

Make requests:
```bash
curl -X POST http://localhost:8000/api/generate-itinerary \
  -H "Content-Type: application/json" \
  -d '{
    "destination": "Paris, France",
    "duration_days": 5,
    "interests": ["culture", "art", "food"],
    "budget": "medium",
    "travel_style": "moderate"
  }'
```

### Option 3: Jupyter Notebook

Open and run `agent-development.ipynb` for interactive testing and examples.

## 📁 Project Structure

```
agent/
├── base_agent.py          # Base agent classes and orchestrator
├── agents.py              # All agent implementations
├── models.py              # Pydantic data models
├── utils.py               # Utility functions (geocoding, distance, etc.)
├── config.py              # Configuration management
├── workflow.py            # Main workflow orchestrator
├── server.py              # FastAPI REST API server
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variable template
├── architecture.md        # Detailed architecture documentation
└── agent-development.ipynb # Development and testing notebook
```

## 🔧 API Endpoints

### Health Check
```
GET /health
```

### Generate Itinerary
```
POST /api/generate-itinerary
```

Request body:
```json
{
  "destination": "Paris, France",
  "origin": "London, UK",
  "duration_days": 5,
  "interests": ["culture", "food", "art"],
  "budget": "medium",
  "travel_style": "moderate",
  "start_date": "2025-12-01"
}
```

### Validate Location
```
POST /api/validate-location
```

### Get Available Interests
```
GET /api/interests
```

## 🧪 Testing

Run the development notebook:
```bash
jupyter notebook agent-development.ipynb
```

The notebook includes:
- Individual agent testing
- Utility function validation
- Complete workflow tests
- Performance benchmarking
- API endpoint testing

## 🔑 API Keys Setup

### Google Maps API
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable APIs: Maps JavaScript API, Places API, Geocoding API
4. Create credentials → API Key
5. Add to `.env` file

### OpenWeather API
1. Sign up at [OpenWeather](https://openweathermap.org/)
2. Get your API key from account settings
3. Add to `.env` file

## 🎯 Anti-Hallucination Strategy

TripGenie implements multiple layers to prevent AI hallucinations:

1. **Input Validation**: Strict JSON schema validation via Pydantic
2. **Real Data**: All facts retrieved from APIs, not generated
3. **Limited LLM Role**: Llama 3 only ranks/structures, doesn't create facts
4. **Schema Enforcement**: Output validated against predefined models
5. **Error Handling**: Graceful fallbacks for each agent

## 🛠️ Development

### Adding a New Agent

1. Create agent class in `agents.py`:
```python
class MyNewAgent(BaseAgent):
    def __init__(self):
        super().__init__("MyNewAgent")
    
    async def process(self, input_data: AgentInput) -> AgentOutput:
        # Your logic here
        return AgentOutput(data={...})
```

2. Add to workflow in `workflow.py`:
```python
self.workflow = SequentialAgent(
    agents=[
        InputValidatorAgent(),
        MyNewAgent(),  # Add here
        RouteExplorerAgent(),
        # ...
    ]
)
```

### Running Tests

```bash
pytest tests/
```

## 📊 Performance

Typical itinerary generation times:
- **3-day trip**: 5-10 seconds
- **5-day trip**: 10-15 seconds
- **7-day trip**: 15-20 seconds

*Times depend on API response times and LLM inference speed*

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Additional agent types (accommodation, dining, transportation)
- More sophisticated LLM prompts
- Frontend UI development
- Caching layer for API responses
- Multi-destination support

## 📄 License

This project is part of TripGenie and follows the repository's license.

## 🔮 Future Enhancements

- [ ] Frontend HTML/Tailwind UI
- [ ] PDF export for itineraries
- [ ] Multi-language support
- [ ] Accommodation booking integration
- [ ] Real-time traffic integration
- [ ] User authentication and saved trips
- [ ] Social features (sharing, reviews)

## 📞 Support

For issues or questions, please refer to `architecture.md` for detailed system documentation.

---

**Built with ❤️ using Google ADK architecture + Llama 3**
