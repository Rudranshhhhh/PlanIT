"""Geo-Location Expert Agent

Handles geocoding, distance calculations, and location-based recommendations.
"""

from typing import Dict, Any, List, Tuple, Optional
import httpx

from agents.base_agent import BaseAgent
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings


class GeoAgent(BaseAgent):
    """Agent for geographic and location-based operations."""

    def __init__(self):
        super().__init__(
            name="Geo-Location Expert",
            description="Handles geocoding, routing, and location-based recommendations.",
        )
        self._cache: Dict[str, Tuple[float, float]] = {}

    @property
    def system_prompt(self) -> str:
        return """You are the Geo-Location Expert agent for PlanIT, a trip planning AI.

Your role is to:
1. Provide geographic information about destinations
2. Suggest optimal routes and travel logistics
3. Recommend nearby attractions and points of interest
4. Estimate travel times between locations
5. Consider geographic constraints (terrain, weather, accessibility)

When providing location advice:
- Consider practical travel times and distances
- Account for local transportation options
- Note geographic features that affect travel
- Suggest logical groupings of nearby attractions

Be specific about locations and provide context about why places are worth visiting.
"""

    async def geocode(self, address: str) -> Optional[Tuple[float, float]]:
        """Get coordinates for an address.
        
        Uses OpenStreetMap Nominatim API (free, no key required).
        
        Returns:
            Tuple of (latitude, longitude) or None if not found.
        """
        # Check cache first
        if address in self._cache:
            return self._cache[address]

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://nominatim.openstreetmap.org/search",
                    params={
                        "q": address,
                        "format": "json",
                        "limit": 1,
                    },
                    headers={"User-Agent": "PlanIT/1.0"},
                    timeout=10.0,
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data:
                        lat = float(data[0]["lat"])
                        lon = float(data[0]["lon"])
                        self._cache[address] = (lat, lon)
                        return (lat, lon)
        except Exception as e:
            print(f"Geocoding error: {e}")
        
        return None

    async def get_place_info(self, place_name: str) -> Dict[str, Any]:
        """Get information about a place using the LLM."""
        response = await self.process(
            f"Provide key geographic and travel information about {place_name}. "
            "Include: location description, best time to visit, main regions/areas, "
            "and any important geographic considerations for travelers."
        )
        
        coords = await self.geocode(place_name)
        
        return {
            "name": place_name,
            "coordinates": coords,
            "description": response,
        }

    async def suggest_itinerary_order(
        self,
        locations: List[str],
        start_location: Optional[str] = None,
    ) -> List[str]:
        """Suggest optimal order to visit locations.
        
        Uses LLM to determine logical ordering based on geography.
        """
        prompt = f"""Given these locations to visit: {', '.join(locations)}
{"Starting from: " + start_location if start_location else ""}

Suggest the optimal order to visit them, considering:
1. Geographic proximity
2. Logical travel flow
3. Time efficiency

Return just the location names in order, one per line."""

        response = await self.llm.chat(
            messages=[{"role": "user", "content": prompt}],
            system_prompt=self.system_prompt,
            temperature=0.3,
        )
        
        # Parse response into list
        ordered = [loc.strip() for loc in response.strip().split("\n") if loc.strip()]
        
        # Filter to only include original locations
        return [loc for loc in ordered if any(orig.lower() in loc.lower() for orig in locations)]

    def calculate_distance(
        self,
        coord1: Tuple[float, float],
        coord2: Tuple[float, float],
    ) -> float:
        """Calculate distance between two coordinates in kilometers.
        
        Uses Haversine formula.
        """
        import math
        
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        
        R = 6371  # Earth's radius in km
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        
        a = (math.sin(dlat / 2) ** 2 +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) ** 2)
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c


if __name__ == "__main__":
    import asyncio

    async def test():
        agent = GeoAgent()
        coords = await agent.geocode("Tokyo, Japan")
        print(f"Tokyo coordinates: {coords}")
        
        if coords:
            osaka_coords = await agent.geocode("Osaka, Japan")
            if osaka_coords:
                dist = agent.calculate_distance(coords, osaka_coords)
                print(f"Tokyo to Osaka: {dist:.1f} km")

    asyncio.run(test())
