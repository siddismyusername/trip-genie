"""
Main orchestration workflow for TripGenie
"""
from base_agent import SequentialAgent
from agents import (
    InputValidatorAgent,
    RouteExplorerAgent,
    DistanceEvaluatorAgent,
    WeatherOptimizerAgent,
    PlaceRankerAgent,
    ItineraryPlannerAgent,
    CostEstimatorAgent
)
from models import UserPreferences, Itinerary
from typing import Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TripGenieWorkflow:
    """
    Main workflow orchestrator for TripGenie
    Chains all agents in sequence following the ADK architecture
    """
    
    def __init__(self):
        # Initialize all agents
        self.workflow = SequentialAgent(
            agents=[
                InputValidatorAgent(),
                RouteExplorerAgent(),
                DistanceEvaluatorAgent(),
                WeatherOptimizerAgent(),
                PlaceRankerAgent(),
                ItineraryPlannerAgent(),
                CostEstimatorAgent()
            ],
            name="TripGenieWorkflow"
        )
        logger.info("TripGenie workflow initialized")
    
    async def generate_itinerary(self, user_preferences: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a complete itinerary from user preferences
        
        Args:
            user_preferences: Dictionary with user preferences
                - destination: str
                - origin: str (optional)
                - duration_days: int
                - interests: List[str]
                - budget: str (low/medium/high)
                - travel_style: str (relaxed/moderate/packed)
                - start_date: str (optional, YYYY-MM-DD)
        
        Returns:
            Dictionary containing the complete itinerary or error
        """
        logger.info("Starting itinerary generation")
        logger.info(f"User preferences: {user_preferences}")
        
        try:
            # Run the workflow
            result = await self.workflow.run(user_preferences)
            
            if not result.success:
                logger.error(f"Workflow failed: {result.error}")
                return {
                    "success": False,
                    "error": result.error
                }
            
            # Extract itinerary
            itinerary_data = result.data.get("itinerary")
            if not itinerary_data:
                return {
                    "success": False,
                    "error": "No itinerary generated"
                }
            
            logger.info("Itinerary generation completed successfully")
            return {
                "success": True,
                "itinerary": itinerary_data,
                "metadata": result.metadata
            }
            
        except Exception as e:
            logger.error(f"Workflow error: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }


# Global workflow instance
tripgenie_workflow = TripGenieWorkflow()


# Convenience function
async def generate_trip_itinerary(
    destination: str,
    duration_days: int,
    interests: list | None = None,
    origin: str | None = None,
    budget: str = "medium",
    travel_style: str = "moderate",
    start_date: str | None = None
) -> Dict[str, Any]:
    """
    Convenience function to generate an itinerary
    
    Args:
        destination: Destination city/location
        duration_days: Trip duration in days (1-30)
        interests: List of interests (default: ["sightseeing", "culture", "food"])
        origin: Starting location (optional)
        budget: Budget level - "low", "medium", or "high" (default: "medium")
        travel_style: Travel pace - "relaxed", "moderate", or "packed" (default: "moderate")
        start_date: Trip start date in YYYY-MM-DD format (optional)
    
    Returns:
        Dictionary with itinerary or error
    """
    if interests is None:
        interests = ["sightseeing", "culture", "food"]
    
    user_prefs = {
        "destination": destination,
        "duration_days": duration_days,
        "interests": interests,
        "budget": budget,
        "travel_style": travel_style
    }
    
    if origin:
        user_prefs["origin"] = origin
    
    if start_date:
        user_prefs["start_date"] = start_date
    
    return await tripgenie_workflow.generate_itinerary(user_prefs)
