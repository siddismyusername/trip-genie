"""
Configuration management for TripGenie
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Keys
    google_maps_api_key: str = ""
    openweather_api_key: str = ""
    
    # Ollama Configuration
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"
    
    # Server Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    
    # Limits
    max_places_per_day: int = 5
    max_travel_distance_km: int = 500
    # Tuning for place discovery
    max_search_queries: int = 5
    max_results_per_query: int = 10
    max_total_places: int = 60

    # Agent orchestration
    agent_timeout_seconds: int = 12

    # Ranking weights
    ranking_relevance_weight: float = 0.6
    ranking_popularity_weight: float = 0.4

    # Weather optimization
    precipitation_avoid_threshold: float = 60.0  # percent
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()
