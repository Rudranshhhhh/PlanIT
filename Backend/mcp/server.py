"""MCP Server for PlanIT.

Exposes travel planning tools via Model Context Protocol (MCP).
This server provides tools that can be used by LLMs to help with travel planning.
"""

import json
from datetime import datetime, timedelta
from typing import Optional
import random


# Tool definitions for MCP
TOOLS = {
    "search_destinations": {
        "name": "search_destinations",
        "description": "Search for travel destinations based on criteria like activities, climate, or budget",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query (e.g., 'beaches in europe', 'adventure travel asia')"
                },
                "budget": {
                    "type": "string",
                    "enum": ["budget", "moderate", "luxury"],
                    "description": "Budget level for the trip"
                },
                "travel_style": {
                    "type": "string",
                    "enum": ["adventure", "relaxation", "cultural", "family", "romantic"],
                    "description": "Type of travel experience"
                }
            },
            "required": ["query"]
        }
    },
    "get_weather_forecast": {
        "name": "get_weather_forecast",
        "description": "Get weather forecast for a destination",
        "inputSchema": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City or location name"
                },
                "date": {
                    "type": "string",
                    "description": "Date in YYYY-MM-DD format"
                }
            },
            "required": ["location"]
        }
    },
    "calculate_trip_budget": {
        "name": "calculate_trip_budget",
        "description": "Calculate estimated budget for a trip",
        "inputSchema": {
            "type": "object",
            "properties": {
                "destination": {
                    "type": "string",
                    "description": "Travel destination"
                },
                "days": {
                    "type": "integer",
                    "description": "Number of travel days"
                },
                "travelers": {
                    "type": "integer",
                    "description": "Number of travelers",
                    "default": 1
                },
                "travel_style": {
                    "type": "string",
                    "enum": ["budget", "moderate", "luxury"],
                    "default": "moderate"
                }
            },
            "required": ["destination", "days"]
        }
    },
    "get_local_attractions": {
        "name": "get_local_attractions",
        "description": "Get popular attractions and activities at a destination",
        "inputSchema": {
            "type": "object",
            "properties": {
                "destination": {
                    "type": "string",
                    "description": "City or destination name"
                },
                "category": {
                    "type": "string",
                    "enum": ["museums", "outdoor", "food", "nightlife", "shopping", "all"],
                    "default": "all"
                }
            },
            "required": ["destination"]
        }
    }
}


# Mock data for destinations
DESTINATIONS_DB = {
    "beaches europe": [
        {"name": "Santorini, Greece", "rating": 4.8, "highlights": ["Stunning sunsets", "White architecture", "Volcanic beaches"]},
        {"name": "Amalfi Coast, Italy", "rating": 4.7, "highlights": ["Dramatic cliffs", "Lemon groves", "Charming villages"]},
        {"name": "Algarve, Portugal", "rating": 4.6, "highlights": ["Golden beaches", "Rock formations", "Affordable"]},
    ],
    "adventure asia": [
        {"name": "Nepal", "rating": 4.9, "highlights": ["Himalayan trekking", "Everest Base Camp", "Buddhist temples"]},
        {"name": "Vietnam", "rating": 4.7, "highlights": ["Ha Long Bay", "Motorbike tours", "Street food"]},
        {"name": "Bali, Indonesia", "rating": 4.6, "highlights": ["Surfing", "Rice terraces", "Temple exploration"]},
    ],
    "cultural": [
        {"name": "Kyoto, Japan", "rating": 4.9, "highlights": ["Ancient temples", "Geisha districts", "Traditional gardens"]},
        {"name": "Rome, Italy", "rating": 4.8, "highlights": ["Colosseum", "Vatican", "Ancient history"]},
        {"name": "Marrakech, Morocco", "rating": 4.5, "highlights": ["Medina", "Souks", "Riad stays"]},
    ]
}

ATTRACTIONS_DB = {
    "paris": {
        "museums": ["Louvre Museum", "Musée d'Orsay", "Centre Pompidou"],
        "outdoor": ["Eiffel Tower", "Luxembourg Gardens", "Seine River Cruise"],
        "food": ["Le Marais Food Tour", "Cooking Class", "Wine Tasting"],
        "nightlife": ["Moulin Rouge", "Jazz Clubs", "Rooftop Bars"],
        "shopping": ["Champs-Élysées", "Le Marais Boutiques", "Galeries Lafayette"]
    },
    "tokyo": {
        "museums": ["Tokyo National Museum", "teamLab Borderless", "Ghibli Museum"],
        "outdoor": ["Senso-ji Temple", "Meiji Shrine", "Shinjuku Gyoen"],
        "food": ["Tsukiji Market", "Ramen Alley", "Izakaya Hopping"],
        "nightlife": ["Shibuya Crossing", "Golden Gai", "Robot Restaurant"],
        "shopping": ["Harajuku", "Akihabara", "Ginza"]
    },
    "default": {
        "museums": ["Local History Museum", "Art Gallery", "Science Center"],
        "outdoor": ["City Park", "Nature Walk", "Viewpoint"],
        "food": ["Local Market", "Food Tour", "Cooking Class"],
        "nightlife": ["Bar District", "Live Music Venue", "Night Market"],
        "shopping": ["Shopping District", "Local Crafts", "Souvenir Shops"]
    }
}

# Budget estimates per day by destination (USD)
BUDGET_RATES = {
    "paris": {"budget": 100, "moderate": 200, "luxury": 450},
    "tokyo": {"budget": 80, "moderate": 180, "luxury": 400},
    "new york": {"budget": 120, "moderate": 250, "luxury": 500},
    "bali": {"budget": 40, "moderate": 100, "luxury": 300},
    "bangkok": {"budget": 35, "moderate": 80, "luxury": 250},
    "default": {"budget": 70, "moderate": 150, "luxury": 350}
}


def search_destinations(query: str, budget: str = "moderate", travel_style: str = None) -> dict:
    """Search for travel destinations."""
    query_lower = query.lower()
    
    # Find matching destinations
    results = []
    for key, destinations in DESTINATIONS_DB.items():
        if any(word in query_lower for word in key.split()):
            results.extend(destinations)
    
    # Fallback to cultural if no match
    if not results:
        results = DESTINATIONS_DB.get("cultural", [])[:2]
    
    return {
        "query": query,
        "budget_level": budget,
        "results": results[:5],
        "total_found": len(results)
    }


def get_weather_forecast(location: str, date: str = None) -> dict:
    """Get weather forecast (simulated)."""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    # Simulated weather data
    weather_types = ["Sunny", "Partly Cloudy", "Cloudy", "Light Rain", "Clear"]
    temp_base = random.randint(15, 28)
    
    return {
        "location": location,
        "date": date,
        "condition": random.choice(weather_types),
        "temperature": {
            "high": temp_base + random.randint(3, 8),
            "low": temp_base - random.randint(3, 8),
            "unit": "°C"
        },
        "humidity": f"{random.randint(40, 80)}%",
        "recommendation": "Good weather for sightseeing" if temp_base > 18 else "Pack layers"
    }


def calculate_trip_budget(destination: str, days: int, travelers: int = 1, 
                          travel_style: str = "moderate", currency: str = "USD") -> dict:
    """Calculate trip budget estimate."""
    dest_lower = destination.lower()
    
    # Base rates in USD
    rates = BUDGET_RATES.get(dest_lower, BUDGET_RATES["default"])
    daily_rate_usd = rates.get(travel_style, rates["moderate"])
    
    # Adjust for India if detected (heuristic)
    is_india = any(x in dest_lower for x in ["india", "mumbai", "delhi", "bangalore", "goa", "chikmagalur", "kerala"])
    
    if currency.upper() == "INR":
        # Conversion rate approx 85 INR/USD, but Indian travel is cheaper than international base rates
        # So we don't just convert, we adjust purchashing power parity roughly
        if is_india:
            # Indian domestic travel rates (manual override for better accuracy)
            if travel_style == "budget": daily_rate = 2500  # Hostel/Homestay + street food
            elif travel_style == "luxury": daily_rate = 15000 # 5-star hotel + flight
            else: daily_rate = 6000 # 3-star hotel + nice meals
        else:
            # International travel in INR
            daily_rate = daily_rate_usd * 86
            
        currency_symbol = "₹"
    else:
        # USD Logic
        daily_rate = daily_rate_usd
        currency_symbol = "$"
    
    # Calculate costs
    accommodation = daily_rate * 0.45 * days
    food = daily_rate * 0.25 * days
    activities = daily_rate * 0.20 * days
    transport = daily_rate * 0.10 * days
    
    subtotal = daily_rate * days
    total = subtotal * travelers
    
    return {
        "destination": destination,
        "days": days,
        "travelers": travelers,
        "travel_style": travel_style,
        "breakdown": {
            "accommodation": f"{currency_symbol}{round(accommodation * travelers):,}",
            "food": f"{currency_symbol}{round(food * travelers):,}",
            "activities": f"{currency_symbol}{round(activities * travelers):,}",
            "local_transport": f"{currency_symbol}{round(transport * travelers):,}"
        },
        "daily_estimate_per_person": f"{currency_symbol}{daily_rate:,}",
        "total_estimate": f"{currency_symbol}{round(total):,}",
        "currency": currency.upper(),
        "note": "Estimated costs excluding major travel tickets (flights/trains) to the destination."
    }


def get_local_attractions(destination: str, category: str = "all") -> dict:
    """Get local attractions for a destination."""
    dest_lower = destination.lower()
    attractions = ATTRACTIONS_DB.get(dest_lower, ATTRACTIONS_DB["default"])
    
    if category == "all":
        all_attractions = []
        for cat, items in attractions.items():
            all_attractions.extend([{"name": item, "category": cat} for item in items])
        return {
            "destination": destination,
            "category": "all",
            "attractions": all_attractions[:10]
        }
    
    items = attractions.get(category, [])
    return {
        "destination": destination,
        "category": category,
        "attractions": [{"name": item, "category": category} for item in items]
    }


def handle_tool_call(tool_name: str, arguments: dict) -> dict:
    """Handle a tool call and return the result."""
    handlers = {
        "search_destinations": search_destinations,
        "get_weather_forecast": get_weather_forecast,
        "calculate_trip_budget": calculate_trip_budget,
        "get_local_attractions": get_local_attractions
    }
    
    handler = handlers.get(tool_name)
    if not handler:
        return {"error": f"Unknown tool: {tool_name}"}
    
    try:
        return handler(**arguments)
    except Exception as e:
        return {"error": str(e)}


def list_tools() -> list:
    """Return list of available tools."""
    return list(TOOLS.values())


# Simple HTTP server for MCP
if __name__ == "__main__":
    from flask import Flask, request, jsonify
    
    app = Flask(__name__)
    
    @app.route("/health")
    def health():
        return jsonify({"status": "ok", "service": "planit-mcp"})
    
    @app.route("/tools", methods=["GET"])
    def get_tools():
        """List available tools."""
        return jsonify({"tools": list_tools()})
    
    @app.route("/tools/call", methods=["POST"])
    def call_tool():
        """Call a tool with arguments."""
        data = request.json
        tool_name = data.get("name")
        arguments = data.get("arguments", {})
        
        if not tool_name:
            return jsonify({"error": "Tool name required"}), 400
        
        result = handle_tool_call(tool_name, arguments)
        return jsonify(result)
    
    print("MCP Server starting on http://127.0.0.1:8001")
    print(f"Available tools: {list(TOOLS.keys())}")
    app.run(host="127.0.0.1", port=8001, debug=True)
