"""Budget Analyst Agent

Analyzes and estimates budgets for trip planning.
"""

from typing import Dict, Any, List, Optional

from agents.base_agent import BaseAgent


class BudgetAgent(BaseAgent):
    """Agent that analyzes and estimates travel budgets."""

    def __init__(self):
        super().__init__(
            name="Budget Analyst",
            description="Estimates costs and creates budget breakdowns for trips.",
        )
        
        # Cost estimation data (could be loaded from a database)
        self._cost_data = {
            "accommodation": {
                "budget": {"min": 20, "max": 50},
                "moderate": {"min": 80, "max": 150},
                "luxury": {"min": 200, "max": 500},
            },
            "food": {
                "budget": {"min": 15, "max": 30},
                "moderate": {"min": 40, "max": 70},
                "luxury": {"min": 100, "max": 200},
            },
            "activities": {
                "budget": {"min": 10, "max": 30},
                "moderate": {"min": 40, "max": 80},
                "luxury": {"min": 100, "max": 300},
            },
            "transport": {
                "budget": {"min": 10, "max": 25},
                "moderate": {"min": 30, "max": 60},
                "luxury": {"min": 80, "max": 150},
            },
        }

    @property
    def system_prompt(self) -> str:
        return """You are the Budget Analyst agent for PlanIT, a trip planning AI.

Your role is to:
1. Estimate costs for travel plans based on destination and preferences
2. Create detailed budget breakdowns (accommodation, food, transport, activities)
3. Suggest ways to optimize spending
4. Flag when plans exceed budget constraints

Provide realistic cost estimates based on:
- Destination cost of living
- Travel style (budget/moderate/luxury)
- Duration of trip
- Group size

Always give ranges when uncertain and explain your assumptions.
Be helpful in suggesting alternatives if budget is tight.
"""

    def estimate_daily_cost(
        self,
        travel_style: str = "moderate",
        destination_multiplier: float = 1.0
    ) -> Dict[str, Dict[str, float]]:
        """Estimate daily costs by category.
        
        Args:
            travel_style: "budget", "moderate", or "luxury"
            destination_multiplier: Cost adjustment for destination (1.0 = average)
            
        Returns:
            Dictionary with min/max estimates for each category.
        """
        style = travel_style.lower() if travel_style else "moderate"
        if style not in ["budget", "moderate", "luxury"]:
            style = "moderate"
        
        result = {}
        for category, styles in self._cost_data.items():
            costs = styles[style]
            result[category] = {
                "min": costs["min"] * destination_multiplier,
                "max": costs["max"] * destination_multiplier,
            }
        
        # Calculate totals
        result["total"] = {
            "min": sum(cat["min"] for cat in result.values()),
            "max": sum(cat["max"] for cat in result.values()),
        }
        
        return result

    def estimate_trip_budget(
        self,
        days: int,
        travel_style: str = "moderate",
        group_size: int = 1,
        destination_multiplier: float = 1.0,
    ) -> Dict[str, Any]:
        """Estimate total trip budget.
        
        Returns:
            Dictionary with daily and total budget estimates.
        """
        daily = self.estimate_daily_cost(travel_style, destination_multiplier)
        
        return {
            "daily_per_person": daily,
            "total_per_person": {
                "min": daily["total"]["min"] * days,
                "max": daily["total"]["max"] * days,
            },
            "total_group": {
                "min": daily["total"]["min"] * days * group_size,
                "max": daily["total"]["max"] * days * group_size,
            },
            "duration_days": days,
            "group_size": group_size,
            "travel_style": travel_style,
        }

    async def analyze_budget(
        self,
        preferences: Dict[str, Any],
        proposed_activities: Optional[List[str]] = None,
    ) -> str:
        """Analyze budget feasibility for given preferences.
        
        Uses LLM to provide detailed budget analysis and recommendations.
        """
        # Build context for LLM
        context = f"""
User preferences:
- Budget: {preferences.get('budget', 'not specified')}
- Duration: {preferences.get('days', 'not specified')} days
- Destination: {preferences.get('destination', 'not specified')}
- Travel style: {preferences.get('travel_style', 'moderate')}
- Group size: {preferences.get('group_size', 1)}

Proposed activities: {proposed_activities or 'none specified'}
"""
        
        return await self.process(
            f"Please analyze if this trip is feasible within budget and provide recommendations.\n{context}"
        )


if __name__ == "__main__":
    # Quick test
    agent = BudgetAgent()
    estimate = agent.estimate_trip_budget(days=7, travel_style="moderate", group_size=2)
    print(f"7-day trip for 2 people (moderate):")
    print(f"  Total: ${estimate['total_group']['min']:.0f} - ${estimate['total_group']['max']:.0f}")
