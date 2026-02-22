"""Tool Registry for Agentic System.

Defines all tools that the ReAct agent can autonomously call.
Each tool has a name, description, parameters, and executor function.
"""

from typing import Dict, Any, List, Callable
import json
try:
    from duckduckgo_search import DDGS
except ImportError:
    from ddgs import DDGS  # Fallback for new package name

# Import tool implementations from MCP server
from mcp.server import (
    search_destinations,
    get_weather_forecast,
    calculate_trip_budget,
    get_local_attractions,
)


# Tool definitions in OpenAI function calling format
TOOL_DEFINITIONS = [
    {
        "name": "search_destinations",
        "description": "Search for travel destinations based on criteria like activities, climate, budget, or travel style. Use this when the user asks for destination recommendations or ideas.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query describing what kind of destination (e.g., 'beaches in europe', 'adventure travel asia', 'romantic getaway')"
                },
                "budget": {
                    "type": "string",
                    "enum": ["budget", "moderate", "luxury"],
                    "description": "Budget level for the trip"
                },
                "travel_style": {
                    "type": "string",
                    "enum": ["adventure", "relaxation", "cultural", "family", "romantic"],
                    "description": "Type of travel experience desired"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_weather",
        "description": "Get weather forecast for a specific destination. Use this when planning activities or deciding what to pack.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City or location name (e.g., 'Paris', 'Tokyo', 'Bali')"
                },
                "date": {
                    "type": "string",
                    "description": "Date in YYYY-MM-DD format (optional, defaults to today)"
                }
            },
            "required": ["location"]
        }
    },
    {
        "name": "calculate_budget",
        "description": "Calculate estimated budget for a trip including accommodation, food, activities, and transport. Always use this when discussing costs or budgets.",
        "parameters": {
            "type": "object",
            "properties": {
                "destination": {
                    "type": "string",
                    "description": "Travel destination city or country"
                },
                "days": {
                    "type": "integer",
                    "description": "Number of travel days"
                },
                "travelers": {
                    "type": "integer",
                    "description": "Number of travelers (default: 1)"
                },
                "travel_style": {
                    "type": "string",
                    "enum": ["budget", "moderate", "luxury"],
                    "description": "Budget style affecting accommodation and activity choices"
                },
                "currency": {
                    "type": "string",
                    "enum": ["USD", "INR"],
                    "description": "Currency for output (e.g., 'INR' for India trips, 'USD' default)"
                }
            },
            "required": ["destination", "days"]
        }
    },
    {
        "name": "get_attractions",
        "description": "Get popular attractions from the INTERNAL database. **WARNING**: Only works for Paris, Tokyo, and New York. For ALL other places (e.g., Mumbai, Chikmagalur), use `search_web` instead.",
        "parameters": {
            "type": "object",
            "properties": {
                "destination": {
                    "type": "string",
                    "description": "City or destination name"
                },
                "category": {
                    "type": "string",
                    "enum": ["museums", "outdoor", "food", "nightlife", "shopping", "all"],
                    "description": "Category of attractions to search for"
                }
            },
            "required": ["destination"]
        }
    },
    {
        "name": "search_knowledge",
        "description": "Search the LOCAL knowledge base. **WARNING**: Only contains limited sample data. DO NOT USE for specific destination planning unless `search_web` failed.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query for travel information"
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "create_itinerary",
        "description": "Generate a detailed day-by-day travel itinerary with morning/afternoon/evening activities, times, and costs. Use this when the user wants a complete trip plan.",
        "parameters": {
            "type": "object",
            "properties": {
                "destination": {
                    "type": "string",
                    "description": "Travel destination"
                },
                "days": {
                    "type": "integer",
                    "description": "Number of days for the trip"
                },
                "budget": {
                    "type": "string",
                    "enum": ["budget", "moderate", "luxury"],
                    "description": "Budget level"
                }
            },
            "required": ["destination", "days"]
        }
    },
    {
        "name": "get_local_tips",
        "description": "Get insider tips, hidden gems, local advice, and money-saving tips from a local expert. Use this to provide authentic, off-the-beaten-path recommendations.",
        "parameters": {
            "type": "object",
            "properties": {
                "destination": {
                    "type": "string",
                    "description": "City or destination name"
                },
                "tip_type": {
                    "type": "string",
                    "enum": ["hidden_gems", "local_tips", "money_saving", "best_times", "all"],
                    "description": "Type of tips to retrieve"
                }
            },
            "required": ["destination"]
        }
    },
    {
        "name": "search_web",
        "description": "Search the live web for real-time information. **PRIMARY TOOL** for finding attractions, hotels, prices, and itineraries for any specific destination (e.g., 'Chikmagalur', 'Mumbai', 'Goa').",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query (e.g., 'top museums in Mumbai', 'entrance fee for Taj Mahal')"
                }
            },
            "required": ["query"]
        }
    }
]


def search_web(query: str) -> Dict[str, Any]:
    """Search the web using DuckDuckGo."""
    try:
        # backend="html" is more robust, but we need to strictly force English/India results
        # "wt-wt" (No region) often defaults to odd results. "in-en" is specific.
        with DDGS() as ddgs:
            results = list(ddgs.text(
                query, 
                max_results=5, 
                backend="html", 
                region="in-en"  # Limit to India (English) region
            ))
            
        if not results:
            # Fallback to no region if specific region fails
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=5, backend="html"))
        
        if not results:
            return {"error": "No results found."}
            
        return {
            "query": query,
            "results": results,
            "source": "web_search"
        }
    except Exception as e:
        print(f"Web search error: {e}")
        return {"error": "Web search currently unavailable. Please try again later."}


def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a tool by name with given arguments.
    
    Args:
        tool_name: Name of the tool to execute
        arguments: Dictionary of arguments for the tool
        
    Returns:
        Tool execution result as a dictionary
    """
    try:
        if tool_name == "search_destinations":
            return search_destinations(
                query=arguments.get("query", ""),
                budget=arguments.get("budget", "moderate"),
                travel_style=arguments.get("travel_style")
            )
        
        elif tool_name == "get_weather":
            return get_weather_forecast(
                location=arguments.get("location", ""),
                date=arguments.get("date")
            )
        
        elif tool_name == "calculate_budget":
            return calculate_trip_budget(
                destination=arguments.get("destination", ""),
                days=arguments.get("days", 1),
                travelers=arguments.get("travelers", 1),
                travel_style=arguments.get("travel_style", "moderate"),
                currency=arguments.get("currency", "USD")
            )
        
        elif tool_name == "get_attractions":
            return get_local_attractions(
                destination=arguments.get("destination", ""),
                category=arguments.get("category", "all")
            )
        
        elif tool_name == "search_knowledge":
            # Use RAG pipeline for knowledge search
            try:
                from rag.rag_pipeline import get_rag_pipeline
                rag = get_rag_pipeline()
                results = rag.retrieve(arguments.get("query", ""), k=3)
                return {
                    "query": arguments.get("query"),
                    "results": [{"text": r["text"], "score": r["score"]} for r in results]
                }
            except Exception as e:
                return {"error": f"Knowledge search unavailable: {str(e)}"}
        
        elif tool_name == "create_itinerary":
            # Use Itinerary Agent
            from agents.itinerary_agent import create_itinerary_agent
            agent = create_itinerary_agent()
            return agent.quick_itinerary(
                destination=arguments.get("destination", ""),
                days=arguments.get("days", 3)
            )
        
        elif tool_name == "get_local_tips":
            # Use Local Expert Agent
            from agents.expert_agent import create_expert_agent
            agent = create_expert_agent()
            tip_type = arguments.get("tip_type", "all")
            destination = arguments.get("destination", "")
            
            if tip_type == "hidden_gems":
                return agent.get_hidden_gems(destination)
            elif tip_type == "local_tips":
                return agent.get_local_tips(destination)
            elif tip_type == "money_saving":
                tips = agent.get_local_tips(destination)
                return {"destination": destination, "money_saving": tips.get("money_saving", [])}
            elif tip_type == "best_times":
                return agent.get_best_times(destination)
            else:
                return agent.get_all_tips(destination)

        elif tool_name == "search_web":
            return search_web(arguments.get("query", ""))
        
        else:
            return {"error": f"Unknown tool: {tool_name}"}
            
    except Exception as e:
        return {"error": str(e)}


def get_tools_prompt() -> str:
    """Generate a prompt describing available tools for the LLM."""
    tools_desc = []
    for tool in TOOL_DEFINITIONS:
        params = tool["parameters"]["properties"]
        param_desc = ", ".join([
            f"{name}: {info.get('description', '')}"
            for name, info in params.items()
        ])
        tools_desc.append(f"- **{tool['name']}**: {tool['description']}\n  Parameters: {param_desc}")
    
    return "\n".join(tools_desc)


def list_tool_names() -> List[str]:
    """Return list of available tool names."""
    return [t["name"] for t in TOOL_DEFINITIONS]

