"""
Data models for TripGenie using Pydantic
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from enum import Enum


class TravelStyle(str, Enum):
    """Travel style preferences"""
    RELAXED = "relaxed"
    MODERATE = "moderate"
    PACKED = "packed"


class Budget(str, Enum):
    """Budget levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class UserPreferences(BaseModel):
    """User input preferences for itinerary generation"""
    destination: str = Field(..., description="Destination city or location")
    origin: Optional[str] = Field(None, description="Starting location (optional)")
    duration_days: int = Field(..., ge=1, le=30, description="Trip duration in days")
    interests: List[str] = Field(default_factory=list, description="User interests (e.g., nature, culture, food)")
    budget: Budget = Field(default=Budget.MEDIUM, description="Budget level")
    travel_style: TravelStyle = Field(default=TravelStyle.MODERATE, description="Travel pace")
    start_date: Optional[date] = Field(None, description="Trip start date")
    
    @validator('interests')
    def validate_interests(cls, v):
        if not v:
            return ["sightseeing", "culture", "food"]
        return [interest.lower().strip() for interest in v]


class Location(BaseModel):
    """Geographic location with coordinates"""
    name: str
    address: str
    latitude: float
    longitude: float
    place_id: Optional[str] = None


class Place(BaseModel):
    """A tourist place or attraction"""
    name: str
    location: Location
    category: str
    rating: Optional[float] = None
    description: Optional[str] = None
    popularity_score: float = 0.0
    relevance_score: float = 0.0
    distance_from_route: Optional[float] = None  # km


class Weather(BaseModel):
    """Weather information for a specific day"""
    date: date
    condition: str
    temperature_max: float
    temperature_min: float
    precipitation_chance: float
    description: str


class Activity(BaseModel):
    """An activity in the itinerary"""
    time: str
    place: Place
    duration_hours: float
    activity_type: str
    notes: Optional[str] = None


class DayItinerary(BaseModel):
    """Itinerary for a single day"""
    day_number: int
    date: date
    weather: Optional[Weather] = None
    activities: List[Activity]
    total_distance_km: float = 0.0
    estimated_cost: Optional[float] = None


class Itinerary(BaseModel):
    """Complete trip itinerary"""
    destination: str
    origin: Optional[str] = None
    start_date: date
    end_date: date
    days: List[DayItinerary]
    total_distance_km: float = 0.0
    estimated_total_cost: Optional[float] = None
    preferences: UserPreferences


class AgentInput(BaseModel):
    """Input data structure for agents"""
    data: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentOutput(BaseModel):
    """Output data structure from agents"""
    data: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    success: bool = True
    error: Optional[str] = None
