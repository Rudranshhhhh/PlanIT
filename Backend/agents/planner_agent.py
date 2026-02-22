"""Planner/Orchestrator Agent

Central agent that coordinates other specialized agents and generates final plans.
"""

from typing import Dict, Any, List, Optional
import json

from agents.base_agent import BaseAgent
from agents.preference_agent import PreferenceAgent
from agents.budget_agent import BudgetAgent
from agents.geo_agent import GeoAgent


class PlannerAgent(BaseAgent):
    """Orchestrator agent that coordinates specialized agents."""

    def __init__(self):
        super().__init__(
            name="Trip Planner",
            description="Orchestrates agents to create comprehensive travel plans.",
        )
        
        # Initialize specialized agents
        self.preference_agent = PreferenceAgent()
        self.budget_agent = BudgetAgent()
        self.geo_agent = GeoAgent()

    @property
    def system_prompt(self) -> str:
        return """You are the Trip Planner orchestrator for PlanIT, an AI travel planning system.

Your role is to:
1. Understand user requests and coordinate with specialized agents
2. Synthesize information from Budget, Geo, and Preference agents
3. Create comprehensive, actionable travel itineraries
4. Ensure plans respect user constraints (budget, time, preferences)

When creating plans:
- Break trips into logical day-by-day itineraries
- Include practical details: times, costs, transport between locations
- Balance activities with rest time
- Consider local factors (weather, opening hours, local customs)

Always be helpful, specific, and provide alternatives when constraints are tight.
Format your itineraries clearly with days, times, and activities.
"""

    async def create_plan(
        self,
        user_message: str,
        existing_preferences: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Create a comprehensive travel plan.
        
        Orchestrates all agents to build a complete itinerary.
        
        Returns:
            Dictionary containing preferences, budget analysis, and itinerary.
        """
        result = {
            "preferences": {},
            "budget_analysis": {},
            "locations": [],
            "itinerary": "",
        }

        # Step 1: Extract preferences if not provided
        if existing_preferences:
            preferences = existing_preferences
        else:
            preferences = await self.preference_agent.extract_preferences(user_message)
        result["preferences"] = preferences

        # Step 2: Get destination info if we have one
        destination = preferences.get("destination")
        if destination:
            location_info = await self.geo_agent.get_place_info(destination)
            result["locations"].append(location_info)

        # Step 3: Budget analysis
        days = 7  # Default
        if preferences.get("dates"):
            dates = preferences["dates"]
            if dates.get("start") and dates.get("end"):
                # Could calculate actual days here
                pass
        
        travel_style = preferences.get("travel_style", "moderate")
        group_size = preferences.get("group_size", 1) or 1
        
        budget_estimate = self.budget_agent.estimate_trip_budget(
            days=days,
            travel_style=travel_style,
            group_size=group_size,
        )
        result["budget_analysis"] = budget_estimate

        # Step 4: Generate the itinerary using LLM with all context
        context = f"""
Based on the following information, create a detailed travel itinerary:

USER REQUEST: {user_message}

EXTRACTED PREFERENCES:
{json.dumps(preferences, indent=2, default=str)}

BUDGET ESTIMATE:
- Daily cost per person: ${budget_estimate['daily_per_person']['total']['min']:.0f}-${budget_estimate['daily_per_person']['total']['max']:.0f}
- Total for group: ${budget_estimate['total_group']['min']:.0f}-${budget_estimate['total_group']['max']:.0f}

Please create a day-by-day itinerary that:
1. Fits within the budget constraints
2. Matches the user's interests
3. Is logistically practical
4. Includes specific recommendations with estimated costs
"""

        itinerary = await self.process(context)
        result["itinerary"] = itinerary

        return result

    async def chat(self, message: str) -> str:
        """Handle a conversational message.
        
        Determines intent and responds appropriately.
        """
        # Check if this is a planning request
        planning_keywords = ["plan", "trip", "travel", "itinerary", "vacation", "visit", "go to"]
        
        if any(kw in message.lower() for kw in planning_keywords):
            # This looks like a planning request
            plan = await self.create_plan(message)
            return plan["itinerary"]
        
        # General conversation
        return await self.process(message)


# Factory function
def create_planner() -> PlannerAgent:
    """Create and return a configured PlannerAgent."""
    return PlannerAgent()


if __name__ == "__main__":
    import asyncio

    async def test():
        planner = PlannerAgent()
        result = await planner.create_plan(
            "Plan a week trip to Japan for 2 people with $4000 budget. "
            "We love food, temples, and want to see both Tokyo and Kyoto."
        )
        print("=== Preferences ===")
        print(json.dumps(result["preferences"], indent=2, default=str))
        print("\n=== Budget ===")
        print(json.dumps(result["budget_analysis"], indent=2, default=str))
        print("\n=== Itinerary ===")
        print(result["itinerary"])

    asyncio.run(test())
