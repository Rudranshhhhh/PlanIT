"""Itinerary Agent - Day-by-Day Travel Plan Generator.

Creates structured, detailed travel itineraries with:
- Morning/afternoon/evening activities
- Transport between locations
- Time estimates
- Cost breakdowns
- Restaurant recommendations
"""

from typing import Dict, Any, List, Optional
import json

from llm_client import get_client


# Sample itinerary data for destinations
DESTINATION_DATA = {
    "paris": {
        "attractions": [
            {"name": "Eiffel Tower", "duration": "2-3 hours", "cost": "$30", "best_time": "morning or sunset"},
            {"name": "Louvre Museum", "duration": "3-4 hours", "cost": "$20", "best_time": "morning"},
            {"name": "Notre-Dame", "duration": "1-2 hours", "cost": "Free", "best_time": "morning"},
            {"name": "Montmartre & Sacré-Cœur", "duration": "3 hours", "cost": "Free", "best_time": "afternoon"},
            {"name": "Champs-Élysées & Arc de Triomphe", "duration": "2-3 hours", "cost": "$15 for Arc", "best_time": "afternoon"},
            {"name": "Seine River Cruise", "duration": "1 hour", "cost": "$20", "best_time": "evening"},
            {"name": "Musée d'Orsay", "duration": "2-3 hours", "cost": "$18", "best_time": "morning"},
            {"name": "Latin Quarter", "duration": "2 hours", "cost": "Free", "best_time": "evening"},
        ],
        "restaurants": [
            {"name": "Le Petit Cler", "cuisine": "French", "price": "$$", "area": "7th arr."},
            {"name": "Bouillon Chartier", "cuisine": "Traditional", "price": "$", "area": "9th arr."},
            {"name": "Pink Mamma", "cuisine": "Italian", "price": "$$", "area": "10th arr."},
        ],
        "transport": "Metro pass €16.90/day, walk most areas"
    },
    "tokyo": {
        "attractions": [
            {"name": "Senso-ji Temple", "duration": "2 hours", "cost": "Free", "best_time": "early morning"},
            {"name": "Shibuya Crossing", "duration": "1 hour", "cost": "Free", "best_time": "evening"},
            {"name": "Meiji Shrine", "duration": "1-2 hours", "cost": "Free", "best_time": "morning"},
            {"name": "teamLab Borderless", "duration": "3 hours", "cost": "$30", "best_time": "afternoon"},
            {"name": "Tsukiji Outer Market", "duration": "2 hours", "cost": "Varies", "best_time": "morning"},
            {"name": "Akihabara", "duration": "3 hours", "cost": "Varies", "best_time": "afternoon"},
            {"name": "Tokyo Skytree", "duration": "2 hours", "cost": "$20", "best_time": "sunset"},
        ],
        "restaurants": [
            {"name": "Ichiran Ramen", "cuisine": "Ramen", "price": "$", "area": "Shibuya"},
            {"name": "Sushi Dai", "cuisine": "Sushi", "price": "$$", "area": "Tsukiji"},
            {"name": "Gonpachi", "cuisine": "Izakaya", "price": "$$", "area": "Roppongi"},
        ],
        "transport": "Suica card, JR Pass if traveling outside"
    },
    "default": {
        "attractions": [
            {"name": "City Center Walk", "duration": "2 hours", "cost": "Free", "best_time": "morning"},
            {"name": "Main Museum", "duration": "3 hours", "cost": "$15", "best_time": "morning"},
            {"name": "Historic District", "duration": "2 hours", "cost": "Free", "best_time": "afternoon"},
            {"name": "Local Market", "duration": "2 hours", "cost": "Varies", "best_time": "morning"},
            {"name": "Viewpoint/Tower", "duration": "1 hour", "cost": "$10", "best_time": "sunset"},
        ],
        "restaurants": [
            {"name": "Local Restaurant", "cuisine": "Local", "price": "$$", "area": "City Center"},
        ],
        "transport": "Public transport or walking"
    }
}


class ItineraryAgent:
    """Agent that generates detailed day-by-day travel itineraries."""
    
    def __init__(self):
        self.llm = get_client()
    
    def get_destination_data(self, destination: str) -> Dict:
        """Get data for a destination."""
        dest_lower = destination.lower()
        return DESTINATION_DATA.get(dest_lower, DESTINATION_DATA["default"])
    
    async def generate_itinerary(
        self,
        destination: str,
        days: int,
        preferences: Optional[Dict] = None,
        budget: str = "moderate"
    ) -> Dict[str, Any]:
        """Generate a detailed day-by-day itinerary.
        
        Args:
            destination: Travel destination
            days: Number of days
            preferences: User preferences (interests, pace, etc.)
            budget: Budget level
            
        Returns:
            Structured itinerary with daily plans
        """
        dest_data = self.get_destination_data(destination)
        
        # Build prompt for LLM
        attractions_info = json.dumps(dest_data["attractions"], indent=2)
        restaurants_info = json.dumps(dest_data["restaurants"], indent=2)
        
        prompt = f"""Create a detailed {days}-day itinerary for {destination}.

AVAILABLE ATTRACTIONS:
{attractions_info}

RESTAURANT RECOMMENDATIONS:
{restaurants_info}

TRANSPORT: {dest_data["transport"]}

USER PREFERENCES: {json.dumps(preferences or {"pace": "moderate", "interests": "general"})}
BUDGET LEVEL: {budget}

Generate a structured itinerary with:
1. Each day clearly labeled (Day 1, Day 2, etc.)
2. Morning, Afternoon, Evening sections
3. Specific times (e.g., "9:00 AM - Visit Eiffel Tower")
4. Transport between locations
5. Meal recommendations
6. Estimated costs

Make it practical and logistically sensible (group nearby attractions).
"""

        messages = [{"role": "user", "content": prompt}]
        system_prompt = "You are an expert travel planner. Create detailed, practical itineraries."
        
        itinerary_text = await self.llm.chat(messages, system_prompt=system_prompt)
        
        return {
            "destination": destination,
            "days": days,
            "budget": budget,
            "itinerary": itinerary_text,
            "transport_tip": dest_data["transport"],
            "restaurants": dest_data["restaurants"]
        }
    
    def quick_itinerary(self, destination: str, days: int) -> Dict[str, Any]:
        """Generate a quick itinerary without LLM (for tool use)."""
        dest_data = self.get_destination_data(destination)
        attractions = dest_data["attractions"]
        
        daily_plans = []
        attraction_idx = 0
        
        for day in range(1, days + 1):
            day_plan = {
                "day": day,
                "morning": [],
                "afternoon": [],
                "evening": []
            }
            
            # Assign 2-3 attractions per day
            for slot in ["morning", "afternoon"]:
                if attraction_idx < len(attractions):
                    day_plan[slot].append(attractions[attraction_idx])
                    attraction_idx += 1
            
            # Evening is usually dinner + light activity
            if attraction_idx < len(attractions):
                day_plan["evening"].append(attractions[attraction_idx])
                attraction_idx += 1
            
            daily_plans.append(day_plan)
        
        return {
            "destination": destination,
            "days": days,
            "daily_plans": daily_plans,
            "restaurants": dest_data["restaurants"],
            "transport": dest_data["transport"]
        }


# Factory function
def create_itinerary_agent() -> ItineraryAgent:
    """Create and return an Itinerary Agent."""
    return ItineraryAgent()
