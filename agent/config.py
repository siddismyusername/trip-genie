"""
Configuration management for TripGenie
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional


# Load .env file located next to this module (agent/.env) first, then fallback to repo root .env
def _load_local_env():
    candidates = [
        Path(__file__).parent / ".env",        # agent/.env
        Path(__file__).parent.parent / ".env", # repo-root .env
        Path.cwd() / ".env"
    ]

    for p in candidates:
        try:
            if p.exists():
                with p.open("r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#") or "=" not in line:
                            continue
                        k, v = line.split("=", 1)
                        k = k.strip()
                        v = v.strip().strip('"').strip("'")
                        # don't overwrite existing environment variables
                        if k and k not in os.environ:
                            os.environ[k] = v
                return
        except Exception:
            # ignore and try next candidate
            continue


_load_local_env()


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
