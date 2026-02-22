"""Preference Interpreter Agent

Extracts and structures user preferences from natural language input.
"""

from typing import Dict, Any, Optional
import json
import re

from agents.base_agent import BaseAgent


class PreferenceAgent(BaseAgent):
    """Agent that interprets user preferences for trip planning."""

    def __init__(self):
        super().__init__(
            name="Preference Interpreter",
            description="Extracts user preferences like budget, dates, interests, and constraints from natural language.",
        )

    @property
    def system_prompt(self) -> str:
        return """You are the Preference Interpreter agent for PlanIT, a trip planning AI.

Your role is to:
1. Extract user preferences from their messages
2. Identify key planning parameters: dates, budget, destinations, interests, constraints
3. Ask clarifying questions when preferences are unclear
4. Structure preferences in a clear format

When extracting preferences, look for:
- Travel dates (start/end dates, duration, flexibility)
- Budget (total budget, daily budget, budget flexibility)
- Destinations (specific places, types of places, regions)
- Interests (activities, cuisine, culture, adventure level)
- Constraints (mobility, dietary, accommodation preferences)
- Group composition (solo, couple, family, group size)

Always respond in a helpful, conversational manner while gathering this information.
If you have enough information, summarize the extracted preferences clearly.
"""

    async def extract_preferences(self, message: str) -> Dict[str, Any]:
        """Extract structured preferences from a user message.
        
        Returns a dictionary with extracted preference fields.
        """
        extraction_prompt = f"""Analyze this message and extract travel preferences.
Return a JSON object with these fields (use null for unknown):
{{
    "destination": "specific place or null",
    "dates": {{"start": "YYYY-MM-DD or null", "end": "YYYY-MM-DD or null", "flexible": true/false}},
    "budget": {{"amount": number or null, "currency": "USD", "per_day": true/false}},
    "interests": ["list", "of", "interests"],
    "constraints": ["list", "of", "constraints"],
    "group_size": number or null,
    "accommodation_type": "hotel/hostel/airbnb/camping or null",
    "travel_style": "budget/moderate/luxury or null"
}}

User message: {message}

Respond ONLY with the JSON object, no other text."""

        response = await self.llm.chat(
            messages=[{"role": "user", "content": extraction_prompt}],
            system_prompt="You are a JSON extraction assistant. Only output valid JSON.",
            temperature=0.3,
        )

        # Try to parse JSON from response
        try:
            # Find JSON in response (handle markdown code blocks)
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

        # Return empty preferences if parsing fails
        return {
            "destination": None,
            "dates": None,
            "budget": None,
            "interests": [],
            "constraints": [],
            "group_size": None,
            "accommodation_type": None,
            "travel_style": None,
        }


if __name__ == "__main__":
    import asyncio

    async def test():
        agent = PreferenceAgent()
        response = await agent.process(
            "I want to plan a week-long trip to Japan in April with a $3000 budget. "
            "I love food, temples, and hiking."
        )
        print(response)

    asyncio.run(test())
