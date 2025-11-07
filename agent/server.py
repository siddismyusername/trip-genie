"""
FastAPI backend server for TripGenie
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
import logging
import uvicorn

from workflow import tripgenie_workflow
from models import UserPreferences, TravelStyle, Budget
from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="TripGenie API",
    description="AI-Powered Itinerary Planner using ADK + Llama 3",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class ItineraryRequest(BaseModel):
    """Request model for itinerary generation"""
    destination: str = Field(..., description="Destination city or location")
    origin: Optional[str] = Field(None, description="Starting location")
    duration_days: int = Field(..., ge=1, le=30, description="Trip duration (1-30 days)")
    interests: List[str] = Field(
        default=["sightseeing", "culture", "food"],
        description="List of interests"
    )
    budget: Budget = Field(default=Budget.MEDIUM, description="Budget level")
    travel_style: TravelStyle = Field(default=TravelStyle.MODERATE, description="Travel pace")
    start_date: Optional[date] = Field(None, description="Trip start date")
    
    class Config:
        json_schema_extra = {
            "example": {
                "destination": "Paris, France",
                "origin": "London, UK",
                "duration_days": 5,
                "interests": ["culture", "food", "art", "history"],
                "budget": "medium",
                "travel_style": "moderate",
                "start_date": "2025-12-01"
            }
        }


class ItineraryResponse(BaseModel):
    """Response model for itinerary generation"""
    success: bool
    itinerary: Optional[dict] = None
    error: Optional[str] = None
    metadata: Optional[dict] = None


# Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "TripGenie API - AI-Powered Itinerary Planner",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "ollama_configured": bool(settings.ollama_base_url),
        "google_maps_configured": bool(settings.google_maps_api_key),
        "openweather_configured": bool(settings.openweather_api_key)
    }


@app.post("/api/generate-itinerary", response_model=ItineraryResponse)
async def generate_itinerary(request: ItineraryRequest):
    """
    Generate a personalized travel itinerary
    
    This endpoint orchestrates multiple AI agents to create a comprehensive
    itinerary based on user preferences, real-time data, and LLM reasoning.
    """
    try:
        logger.info(f"Received itinerary request for {request.destination}")
        
        # Convert request to dictionary
        user_prefs = request.dict()
        
        # Generate itinerary using the workflow
        result = await tripgenie_workflow.generate_itinerary(user_prefs)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result.get("error", "Unknown error"))
        
        logger.info("Itinerary generated successfully")
        return ItineraryResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating itinerary: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/autocomplete-location")
async def autocomplete_location(query: str):
    """
    Get location autocomplete suggestions
    
    Returns location suggestions based on user input using Google Places Autocomplete API
    """
    from utils import fetch_location_suggestions
    
    try:
        if not query or len(query.strip()) < 2:
            return {
                "success": True,
                "suggestions": []
            }
        
        suggestions = fetch_location_suggestions(query)
        
        return {
            "success": True,
            "suggestions": suggestions
        }
    except Exception as e:
        logger.error(f"Error fetching location suggestions: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/validate-location")
async def validate_location(location: str):
    """
    Validate and geocode a location
    
    Useful for frontend to validate user input before submitting
    """
    from utils import geocode_location
    
    try:
        location_data = geocode_location(location)
        if not location_data:
            raise HTTPException(status_code=404, detail="Location not found")
        
        return {
            "success": True,
            "location": location_data
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating location: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/interests")
async def get_available_interests():
    """
    Get list of available interest categories
    """
    interests = [
        "nature", "culture", "food", "art", "history", "adventure",
        "nightlife", "shopping", "beaches", "mountains", "museums",
        "architecture", "photography", "wildlife", "sports"
    ]
    return {"interests": interests}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else "An error occurred"
        }
    )


def start_server():
    """Start the FastAPI server"""
    logger.info(f"Starting TripGenie API server on {settings.api_host}:{settings.api_port}")
    uvicorn.run(
        "server:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
        log_level="info"
    )


if __name__ == "__main__":
    start_server()
