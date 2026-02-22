"""Local Expert Agent - Insider Tips and Hidden Gems.

Provides local knowledge like:
- Hidden gems & local favorites
- Best times to visit attractions
- Money-saving tips
- Cultural etiquette
- Food recommendations
- Safety tips
"""

from typing import Dict, Any, List, Optional
import json

from llm_client import get_client


# Local expert knowledge database
LOCAL_KNOWLEDGE = {
    "paris": {
        "hidden_gems": [
            "Promenade Plantée - Elevated park that inspired NYC's High Line, rarely crowded",
            "Canal Saint-Martin - Trendy area with cute cafes, perfect for afternoon stroll",
            "Rue Crémieux - Colorful street perfect for photos, locals-only vibe",
            "Shakespeare and Company - Historic bookstore, free readings upstairs",
            "Marché des Enfants Rouges - Oldest covered market, amazing food stalls",
        ],
        "local_tips": [
            "Say 'Bonjour' when entering any shop - it's considered rude not to",
            "Metro tickets are cheaper in carnets (books of 10)",
            "Many museums are free on the first Sunday of each month",
            "Parisians eat dinner late (8-9 PM), lunch is usually 12-2 PM",
            "Tipping is not expected but rounding up is appreciated",
        ],
        "money_saving": [
            "Paris Museum Pass saves money if visiting 3+ museums",
            "Picnic in parks - buy baguettes, cheese, and wine from local shops",
            "Walk! Paris is very walkable and you'll discover more",
            "Avoid restaurants right next to major attractions - walk 2 blocks for better prices",
        ],
        "safety": [
            "Watch for pickpockets at Eiffel Tower, Louvre, and Metro",
            "Keep bags zipped and in front of you",
            "Generally very safe, but avoid northern suburbs at night",
        ],
        "best_times": {
            "Eiffel Tower": "Go at sunset for magical views and fewer crowds",
            "Louvre": "Wednesday/Friday evenings - open late, much quieter",
            "Notre-Dame": "Early morning for photos without crowds",
            "Montmartre": "Weekday mornings to avoid weekend crowds",
        }
    },
    "tokyo": {
        "hidden_gems": [
            "Yanaka district - Old Tokyo atmosphere, traditional shops, Yanaka Cemetery for peaceful walks",
            "Shimokitazawa - Vintage shops, indie cafes, bohemian vibe",
            "Golden Gai - Tiny bars in Shinjuku, incredibly atmospheric",
            "Omoide Yokocho - Piss Alley yakitori stands, authentic old Tokyo",
            "Nezu Shrine - Beautiful shrine with tunnel of torii gates, less crowded than Fushimi Inari",
        ],
        "local_tips": [
            "Always carry cash - many places don't accept cards",
            "Bow slightly when thanking (especially in traditional settings)",
            "Don't eat while walking - find a spot to stand or sit",
            "Remove shoes when entering homes, some restaurants, temples",
            "Trains are extremely punctual - if it says 10:03, it leaves at 10:03",
        ],
        "money_saving": [
            "Convenience store food (7-Eleven, Lawson) is surprisingly good and cheap",
            "Get a Suica card for easy transport payment",
            "100-yen shops are great for snacks and souvenirs",
            "Lunch sets (teishoku) are much cheaper than dinner",
            "Free activities: shrines, temples, walking neighborhoods",
        ],
        "safety": [
            "Tokyo is extremely safe, even at night",
            "Biggest 'danger' is getting lost in train stations",
            "Keep valuables safe but crime is very rare",
        ],
        "best_times": {
            "Senso-ji Temple": "Before 7 AM for empty photos",
            "Tsukiji Market": "8-10 AM for fresh food, avoid Mondays",
            "Shibuya Crossing": "Evening for full energy and lights",
            "teamLab": "Book 2+ weeks ahead, go on weekdays",
        }
    },
    "default": {
        "hidden_gems": [
            "Ask locals for their favorite neighborhood restaurant",
            "Visit the local market for authentic experience",
            "Walk through residential areas for real local life",
        ],
        "local_tips": [
            "Learn basic greetings in the local language",
            "Research local customs and etiquette before arriving",
            "Carry local currency for small purchases",
        ],
        "money_saving": [
            "Eat where locals eat, away from tourist areas",
            "Use public transportation",
            "Look for free walking tours",
        ],
        "safety": [
            "Keep copies of important documents",
            "Register with your embassy for emergencies",
            "Know emergency numbers",
        ],
        "best_times": {}
    }
}


class LocalExpertAgent:
    """Agent that provides insider tips and local knowledge."""
    
    def __init__(self):
        self.llm = get_client()
    
    def get_destination_knowledge(self, destination: str) -> Dict:
        """Get local knowledge for a destination."""
        dest_lower = destination.lower()
        return LOCAL_KNOWLEDGE.get(dest_lower, LOCAL_KNOWLEDGE["default"])
    
    def get_hidden_gems(self, destination: str) -> Dict[str, Any]:
        """Get hidden gems for a destination."""
        knowledge = self.get_destination_knowledge(destination)
        return {
            "destination": destination,
            "hidden_gems": knowledge["hidden_gems"],
            "tip": "These are places locals love but tourists often miss!"
        }
    
    def get_local_tips(self, destination: str) -> Dict[str, Any]:
        """Get local tips and etiquette."""
        knowledge = self.get_destination_knowledge(destination)
        return {
            "destination": destination,
            "local_tips": knowledge["local_tips"],
            "money_saving": knowledge["money_saving"],
            "safety": knowledge["safety"]
        }
    
    def get_best_times(self, destination: str) -> Dict[str, Any]:
        """Get best times to visit attractions."""
        knowledge = self.get_destination_knowledge(destination)
        return {
            "destination": destination,
            "best_times": knowledge.get("best_times", {}),
            "general_tip": "Early morning and weekdays are usually less crowded"
        }
    
    def get_all_tips(self, destination: str) -> Dict[str, Any]:
        """Get all local expert tips for a destination."""
        knowledge = self.get_destination_knowledge(destination)
        return {
            "destination": destination,
            "hidden_gems": knowledge["hidden_gems"],
            "local_tips": knowledge["local_tips"],
            "money_saving": knowledge["money_saving"],
            "safety": knowledge["safety"],
            "best_times": knowledge.get("best_times", {})
        }
    
    async def ask_expert(self, destination: str, question: str) -> str:
        """Ask the local expert a specific question using LLM."""
        knowledge = self.get_destination_knowledge(destination)
        
        context = f"""You are a local expert for {destination}. 
        
Here's your knowledge base:
- Hidden gems: {json.dumps(knowledge['hidden_gems'])}
- Local tips: {json.dumps(knowledge['local_tips'])}
- Money saving: {json.dumps(knowledge['money_saving'])}
- Safety: {json.dumps(knowledge['safety'])}
- Best times: {json.dumps(knowledge.get('best_times', {}))}

Answer the user's question with insider knowledge and practical tips.
"""
        
        messages = [{"role": "user", "content": question}]
        return await self.llm.chat(messages, system_prompt=context)


# Factory function
def create_expert_agent() -> LocalExpertAgent:
    """Create and return a Local Expert Agent."""
    return LocalExpertAgent()
