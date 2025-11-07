"""
Agent implementations for TripGenie
"""
from base_agent import BaseAgent, LLMAgent
from models import (
    AgentInput, AgentOutput, UserPreferences, Location, Place, 
    Weather, Activity, DayItinerary, Itinerary
)
from utils import (
    geocode_location, fetch_google_places, fetch_place_details,
    fetch_google_weather_forecast, haversine_distance, is_point_on_route,
    calculate_route_distance
)
from datetime import datetime, timedelta, date
from typing import List, Dict, Any, Optional
import logging
import json

logger = logging.getLogger(__name__)


class InputValidatorAgent(BaseAgent):
    """Validates and normalizes user inputs, fetches geolocation data"""
    
    def __init__(self):
        super().__init__("InputValidator")
    
    async def process(self, input_data: AgentInput) -> AgentOutput:
        """Validate user preferences and geocode locations"""
        
        # Parse user preferences
        try:
            prefs = UserPreferences(**input_data.data)
        except Exception as e:
            return AgentOutput(
                data={},
                success=False,
                error=f"Invalid user preferences: {str(e)}"
            )
        
        # Geocode destination
        destination_data = geocode_location(prefs.destination)
        if not destination_data:
            return AgentOutput(
                data={},
                success=False,
                error=f"Could not geocode destination: {prefs.destination}"
            )
        
        destination_location = Location(**destination_data)
        
        # Geocode origin if provided
        origin_location = None
        if prefs.origin:
            origin_data = geocode_location(prefs.origin)
            if origin_data:
                origin_location = Location(**origin_data)
        
        # Set start date if not provided
        if not prefs.start_date:
            prefs.start_date = date.today() + timedelta(days=7)
        
        return AgentOutput(
            data={
                "preferences": prefs.dict(),
                "destination_location": destination_location.dict(),
                "origin_location": origin_location.dict() if origin_location else None
            },
            metadata={
                "validated": True,
                "geocoded": True
            }
        )


class RouteExplorerAgent(BaseAgent):
    """Finds tourist attractions along the route or near destination"""
    
    def __init__(self):
        super().__init__("RouteExplorer")
    
    async def process(self, input_data: AgentInput) -> AgentOutput:
        """Find places of interest"""
        
        prefs = UserPreferences(**input_data.data["preferences"])
        dest_location = Location(**input_data.data["destination_location"])
        
        # Build search queries based on interests
        search_queries = []
        for interest in prefs.interests:
            search_queries.append(f"{interest} in {dest_location.name}")
        
        # Also add general tourist attractions
        search_queries.append(f"tourist attractions in {dest_location.name}")
        search_queries.append(f"things to do in {dest_location.name}")
        
        # Fetch places
        all_places = []
        seen_place_ids = set()
        
        from config import settings
        max_queries = settings.max_search_queries
        max_per_query = settings.max_results_per_query
        max_total = settings.max_total_places

        for query in search_queries[:max_queries]:  # Tunable via settings
            if len(all_places) >= max_total:
                break
            places_data = fetch_google_places(
                query,
                location=(dest_location.latitude, dest_location.longitude)
            )

            for place_data in places_data[:max_per_query]:  # Tunable per query
                if len(all_places) >= max_total:
                    break
                place_id = place_data.get("place_id")
                if place_id in seen_place_ids:
                    continue
                seen_place_ids.add(place_id)
                
                # Create Place object
                place = Place(
                    name=place_data.get("name", "Unknown"),
                    location=Location(
                        name=place_data.get("name", "Unknown"),
                        address=place_data.get("formatted_address", ""),
                        latitude=place_data["geometry"]["location"]["lat"],
                        longitude=place_data["geometry"]["location"]["lng"],
                        place_id=place_id
                    ),
                    category=", ".join(place_data.get("types", [])[:3]),
                    rating=place_data.get("rating"),
                    description=place_data.get("vicinity", "")
                )
                
                all_places.append(place.dict())
        
        logger.info(f"Found {len(all_places)} unique places")
        
        return AgentOutput(
            data={
                **input_data.data,
                "places": all_places
            },
            metadata={
                "places_count": len(all_places)
            }
        )


class DistanceEvaluatorAgent(BaseAgent):
    """Calculates distances between locations and prunes outliers"""
    
    def __init__(self):
        super().__init__("DistanceEvaluator")
    
    async def process(self, input_data: AgentInput) -> AgentOutput:
        """Calculate distances and filter places"""
        
        dest_location = Location(**input_data.data["destination_location"])
        places = [Place(**p) for p in input_data.data["places"]]
        prefs = UserPreferences(**input_data.data["preferences"])
        
        # Calculate distance from destination for each place
        for place in places:
            distance = haversine_distance(
                dest_location.latitude,
                dest_location.longitude,
                place.location.latitude,
                place.location.longitude
            )
            place.distance_from_route = distance
        
        # Filter out places too far away (based on trip duration)
        # Travel style adjustments
        base_distance = prefs.duration_days * 40  # conservative base
        style_multiplier = {
            "relaxed": 0.8,
            "moderate": 1.0,
            "packed": 1.3
        }.get(prefs.travel_style.value, 1.0)
        max_distance = min(int(base_distance * style_multiplier), 200)
        filtered_places = [
            p for p in places 
            if p.distance_from_route is not None and p.distance_from_route <= max_distance
        ]
        
        # Sort by distance
        filtered_places.sort(key=lambda x: x.distance_from_route or 0)
        
        logger.info(f"Filtered to {len(filtered_places)} places within {max_distance}km")
        
        return AgentOutput(
            data={
                **input_data.data,
                "places": [p.dict() for p in filtered_places]
            },
            metadata={
                "filtered_count": len(filtered_places),
                "max_distance_km": max_distance
            }
        )


class WeatherOptimizerAgent(BaseAgent):
    """Adjusts itinerary based on weather forecasts"""
    
    def __init__(self):
        super().__init__("WeatherOptimizer")
    
    async def process(self, input_data: AgentInput) -> AgentOutput:
        """Fetch weather and categorize days"""
        
        dest_location = Location(**input_data.data["destination_location"])
        prefs = UserPreferences(**input_data.data["preferences"])
        
        # Fetch weather forecast
        weather_data = fetch_google_weather_forecast(
            dest_location.latitude,
            dest_location.longitude,
            days=prefs.duration_days
        )
        
        # Process weather by day
        daily_weather = []
        current_date = prefs.start_date
        
        if not current_date:
            current_date = date.today()
        
        if weather_data:
            # Group by day (weather API gives 3-hour intervals)
            for day_offset in range(prefs.duration_days):
                day_date = current_date + timedelta(days=day_offset)
                
                # Find weather data for this day (simplified)
                if day_offset * 8 < len(weather_data):
                    day_forecast = weather_data[day_offset * 8]
                    weather = Weather(
                        date=day_date,
                        condition=day_forecast["weather"][0]["main"],
                        temperature_max=day_forecast["main"]["temp_max"],
                        temperature_min=day_forecast["main"]["temp_min"],
                        precipitation_chance=day_forecast.get("pop", 0) * 100,
                        description=day_forecast["weather"][0]["description"]
                    )
                    daily_weather.append(weather.dict())
        
        return AgentOutput(
            data={
                **input_data.data,
                "weather_forecast": daily_weather
            },
            metadata={
                "weather_days": len(daily_weather)
            }
        )


class PlaceRankerAgent(LLMAgent):
    """Ranks places using Llama 3 based on popularity and relevance"""
    
    def __init__(self):
        super().__init__("PlaceRanker")
    
    async def process(self, input_data: AgentInput) -> AgentOutput:
        """Rank places using LLM"""
        
        places = [Place(**p) for p in input_data.data["places"]]
        prefs = UserPreferences(**input_data.data["preferences"])
        
        # Create prompt for LLM
        places_info = "\n".join([
            f"{i+1}. {p.name} - {p.category} (Rating: {p.rating or 'N/A'})"
            for i, p in enumerate(places[:30])  # Limit to top 30
        ])
        
        system_prompt = """You are a travel expert. Score tourist places based on:
1. Popularity and ratings
2. Relevance to user interests
3. Uniqueness and must-see factor

Return ONLY a JSON array of scores (0-100) in the same order as the input places."""
        
        user_prompt = f"""User interests: {', '.join(prefs.interests)}
Travel style: {prefs.travel_style}
Budget: {prefs.budget}

Places to rank:
{places_info}

Return a JSON array of scores (0-100) for each place, in order."""
        
        try:
            response = await self.call_llm(user_prompt, system_prompt)
            
            # Parse scores from response
            # Try to extract JSON array
            import re
            json_match = re.search(r'\[[\d,\s]+\]', response)
            if json_match:
                scores = json.loads(json_match.group())
            else:
                # Fallback: use ratings
                scores = [(p.rating or 0) * 20 for p in places[:30]]
            
            # Assign scores
            for i, place in enumerate(places[:len(scores)]):
                place.relevance_score = scores[i]
                place.popularity_score = (place.rating or 0) * 20
            
            from config import settings
            rw = settings.ranking_relevance_weight
            pw = settings.ranking_popularity_weight
            places.sort(
                key=lambda x: (x.relevance_score * rw + x.popularity_score * pw),
                reverse=True
            )
            
        except Exception as e:
            logger.warning(f"LLM ranking failed, using ratings: {e}")
            # Fallback to rating-based ranking
            for place in places:
                place.popularity_score = (place.rating or 0) * 20
                place.relevance_score = place.popularity_score
            from config import settings
            rw = settings.ranking_relevance_weight
            pw = settings.ranking_popularity_weight
            places.sort(
                key=lambda x: (x.relevance_score * rw + x.popularity_score * pw),
                reverse=True
            )
        
        return AgentOutput(
            data={
                **input_data.data,
                "places": [p.dict() for p in places]
            },
            metadata={
                "ranked": True
            }
        )


class ItineraryPlannerAgent(LLMAgent):
    """Generates day-wise itinerary using Llama 3"""
    
    def __init__(self):
        super().__init__("ItineraryPlanner")
    
    async def process(self, input_data: AgentInput) -> AgentOutput:
        """Generate structured itinerary"""
        
        prefs = UserPreferences(**input_data.data["preferences"])
        places = [Place(**p) for p in input_data.data["places"]]
        weather_forecast = [Weather(**w) for w in input_data.data.get("weather_forecast", [])]
        dest_location = Location(**input_data.data["destination_location"])
        
        # Ensure start_date is set
        if not prefs.start_date:
            prefs.start_date = date.today()
        
        # Select top places based on duration
        max_places = prefs.duration_days * 4  # ~4 activities per day
        top_places = places[:max_places]
        
        # Create itinerary structure with weather-aware ordering
        days = []
        current_date = prefs.start_date
        places_per_day = len(top_places) // prefs.duration_days if prefs.duration_days > 0 else 0

        # Weather-based reordering: move outdoor (heuristic) activities to low precipitation days
        from config import settings
        precip_threshold = settings.precipitation_avoid_threshold
        outdoor_place_names = set()
        for p in top_places:
            if any(k in p.category.lower() for k in ["park", "trail", "outdoor", "beach", "garden", "mountain"]):
                outdoor_place_names.add(p.name)

        # Sort weather days by precipitation chance ascending
        sorted_weather_dates = []
        if weather_forecast:
            sorted_weather_dates = sorted(weather_forecast, key=lambda w: w.precipitation_chance)

        # Assign outdoor-heavy sets to best weather days
        if sorted_weather_dates and outdoor_place_names:
            # naive redistribution: ensure outdoor places are placed earlier on low-rain days
            top_places.sort(
                key=lambda p: (
                    0 if p.name in outdoor_place_names else 1,
                    p.relevance_score * -1
                )
            )
        
        for day_num in range(prefs.duration_days):
            start_idx = day_num * places_per_day
            end_idx = start_idx + places_per_day
            day_places = top_places[start_idx:end_idx]
            
            # Get weather for this day
            day_weather = None
            if current_date:
                target_date = current_date + timedelta(days=day_num)
                for w in weather_forecast:
                    if w.date == target_date:
                        day_weather = w
                        break
            
            # Create activities
            activities = []
            current_time = "09:00"
            
            for place in day_places:
                activity = Activity(
                    time=current_time,
                    place=place,
                    duration_hours=2.0,
                    activity_type="outdoor" if place.name in outdoor_place_names else "sightseeing",
                    notes=f"Visit {place.name}"
                )
                activities.append(activity)
                
                # Increment time
                hour = int(current_time.split(":")[0]) + 3
                current_time = f"{hour:02d}:00"
            
            day_itinerary = DayItinerary(
                day_number=day_num + 1,
                date=current_date + timedelta(days=day_num),
                weather=day_weather,
                activities=activities,
                total_distance_km=0.0
            )
            days.append(day_itinerary)
        
        # Create full itinerary
        origin_loc = input_data.data.get("origin_location")
        origin_name = origin_loc.get("name") if origin_loc else None
        
        itinerary = Itinerary(
            destination=dest_location.name,
            origin=origin_name,
            start_date=prefs.start_date,
            end_date=prefs.start_date + timedelta(days=prefs.duration_days - 1),
            days=days,
            preferences=prefs
        )
        
        return AgentOutput(
            data={
                **input_data.data,
                "itinerary": itinerary.dict()
            },
            metadata={
                "itinerary_generated": True
            }
        )


class CostEstimatorAgent(BaseAgent):
    """Estimates per-activity and total trip cost using simple heuristics"""

    def __init__(self):
        super().__init__("CostEstimator")

    async def process(self, input_data: AgentInput) -> AgentOutput:
        itinerary_data = input_data.data.get("itinerary")
        if not itinerary_data:
            return AgentOutput(data=input_data.data, success=False, error="No itinerary to cost estimate")

        from models import Itinerary, DayItinerary, Activity, Place
        from config import settings
        prefs = itinerary_data.get("preferences", {})
        itinerary = Itinerary(**itinerary_data)

        # Simple category-based cost mapping (local currency heuristic not implemented yet)
        base_map = {
            "museum": 20,
            "park": 0,
            "gallery": 15,
            "historic": 25,
            "restaurant": 30,
            "sightseeing": 10,
            "outdoor": 5
        }
        budget_multiplier = {
            "low": 0.8,
            "medium": 1.0,
            "high": 1.4
        }.get(itinerary.preferences.budget.value, 1.0)

        total_cost = 0.0
        updated_days = []
        for day in itinerary.days:
            day_cost = 0.0
            updated_activities = []
            for act in day.activities:
                cat = act.place.category.lower()
                # pick first matching key
                cost_base = 10
                for k, v in base_map.items():
                    if k in cat:
                        cost_base = v
                        break
                activity_cost = cost_base * budget_multiplier
                act_dict = act.dict()
                act_dict["estimated_cost"] = round(activity_cost, 2)
                day_cost += activity_cost
                updated_activities.append(act_dict)
            day_dict = day.dict()
            day_dict["activities"] = updated_activities
            day_dict["estimated_cost"] = round(day_cost, 2)
            total_cost += day_cost
            updated_days.append(day_dict)

        itinerary_dict = itinerary.dict()
        itinerary_dict["days"] = updated_days
        itinerary_dict["estimated_total_cost"] = round(total_cost, 2)

        return AgentOutput(
            data={**input_data.data, "itinerary": itinerary_dict},
            metadata={"cost_estimated": True, "total_cost": round(total_cost, 2)}
        )
