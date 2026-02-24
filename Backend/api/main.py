"""Flask API server for PlanIT."""

import os
import sys
import asyncio

# Add parent directory to path so we can import Backend modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify
from flask_cors import CORS

from config import settings
from agents.planner_agent import PlannerAgent
from memory.session_store import get_session_store
from auth import create_user, authenticate_user

app = Flask(__name__)
CORS(app)

# Global store and per-session planners
session_store = get_session_store()
planners = {}  # session_id -> PlannerAgent


def get_planner(session_id: str) -> PlannerAgent:
    """Get or create a PlannerAgent for a session."""
    if session_id not in planners:
        planners[session_id] = PlannerAgent()
    return planners[session_id]


# ─── Health ───────────────────────────────────────────────
@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "planit-api"})


# ─── Auth ─────────────────────────────────────────────────
@app.route("/auth/signup", methods=["POST"])
def signup():
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not name or not email or not password:
        return jsonify({"error": "Name, email, and password are required."}), 400

    try:
        user = create_user(name, email, password)
        return jsonify({"user": user}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 409


@app.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = data.get("email", "").strip()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    user = authenticate_user(email, password)
    if not user:
        return jsonify({"error": "Invalid email or password."}), 401

    return jsonify({"user": user}), 200


@app.route("/auth/google", methods=["POST"])
def google_login():
    """Upsert a Google-authenticated user into MongoDB."""
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    email = data.get("email", "").strip()

    if not email:
        return jsonify({"error": "Email is required."}), 400

    from auth import _users  # reuse the collection

    # Upsert: create if new, return existing if already there
    existing = _users.find_one({"email": email})
    if existing:
        return jsonify({"user": {"name": existing["name"], "email": existing["email"]}}), 200

    _users.insert_one({
        "name": name or email.split("@")[0],
        "email": email,
        "password": None,  # Google users have no local password
    })
    return jsonify({"user": {"name": name or email.split("@")[0], "email": email}}), 201


# ─── Weather ──────────────────────────────────────────────
@app.route("/weather/<destination>")
def weather(destination):
    """Fetch current weather + 5-day forecast from OpenWeatherMap."""
    import requests as req

    api_key = "f912cbbaac29b1aafe1c2fca56e3d628"

    # Current weather (also gives us lat/lon)
    current_url = f"https://api.openweathermap.org/data/2.5/weather?q={destination}&appid={api_key}&units=metric"
    current_resp = req.get(current_url, timeout=10)
    if current_resp.status_code != 200:
        return jsonify({"error": f"Could not find weather for '{destination}'"}), 404

    current = current_resp.json()
    lat = current["coord"]["lat"]
    lon = current["coord"]["lon"]

    # 5-day / 3-hour forecast
    forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric&cnt=40"
    forecast_resp = req.get(forecast_url, timeout=10)
    forecast_data = forecast_resp.json() if forecast_resp.status_code == 200 else {}

    # Extract one forecast per day (noon readings)
    daily = []
    seen_dates = set()
    for item in forecast_data.get("list", []):
        date = item["dt_txt"].split(" ")[0]
        hour = item["dt_txt"].split(" ")[1]
        if date not in seen_dates and "12:00" in hour:
            seen_dates.add(date)
            daily.append({
                "date": date,
                "temp": round(item["main"]["temp"]),
                "temp_min": round(item["main"]["temp_min"]),
                "temp_max": round(item["main"]["temp_max"]),
                "description": item["weather"][0]["description"],
                "icon": item["weather"][0]["icon"],
            })

    return jsonify({
        "current": {
            "temp": round(current["main"]["temp"]),
            "feels_like": round(current["main"]["feels_like"]),
            "humidity": current["main"]["humidity"],
            "description": current["weather"][0]["description"],
            "icon": current["weather"][0]["icon"],
            "wind_speed": current.get("wind", {}).get("speed", 0),
        },
        "forecast": daily[:5],
        "coords": {"lat": lat, "lon": lon},
        "city": current.get("name", destination),
    })


# ─── Session Management ──────────────────────────────────
@app.route("/session/create", methods=["POST"])
def create_session():
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    session = session_store.create_session(user_id=user_id)
    return jsonify({
        "session_id": session.session_id,
        "created_at": session.created_at.isoformat(),
    })


@app.route("/session/<session_id>/history")
def session_history(session_id):
    session = session_store.get_session(session_id)
    if not session:
        return jsonify({"error": "Session not found or expired"}), 404
    return jsonify({
        "session_id": session.session_id,
        "messages": session.messages,
        "context": session.context,
    })


# ─── Chat ─────────────────────────────────────────────────
@app.route("/session/<session_id>/chat", methods=["POST"])
def chat(session_id):
    session = session_store.get_session(session_id)
    if not session:
        return jsonify({"error": "Session not found or expired"}), 404

    data = request.get_json()
    message = data.get("message", "")
    if not message:
        return jsonify({"error": "Message is required"}), 400

    # Record user message
    session.add_message("user", message)

    try:
        planner = get_planner(session_id)
        response_text = asyncio.run(planner.chat(message))

        # Record bot response
        session.add_message("assistant", response_text)

        return jsonify({
            "response": response_text,
            "tool_calls": [],
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─── Structured Trip Planner ──────────────────────────────
@app.route("/plan", methods=["POST"])
def plan_trip():
    """Generate a trip plan from structured form data."""
    data = request.get_json()

    destination = data.get("destination", "")
    days = data.get("days", 3)
    start_date = data.get("start_date", "")
    budget = data.get("budget", 0)
    travelers = data.get("travelers", 1)
    travel_style = data.get("travel_style", "moderate")
    interests = data.get("interests", [])

    if not destination:
        return jsonify({"error": "Destination is required"}), 400

    # Build a natural-language prompt from the structured inputs
    interests_str = ", ".join(interests) if interests else "general sightseeing"
    prompt = (
        f"Plan a detailed {days}-day trip to {destination} "
        f"for {travelers} traveler{'s' if travelers > 1 else ''}. "
    )
    if start_date:
        prompt += f"Starting on {start_date}. "
    if budget:
        prompt += f"Total budget is ₹{budget:,}. "
    prompt += (
        f"Travel style: {travel_style}. "
        f"Interests: {interests_str}. "
        f"Please provide a day-by-day itinerary with specific places, "
        f"timings, estimated costs in INR, and practical tips. "
        f"Format each day clearly with a title and activities."
    )

    try:
        planner = PlannerAgent()
        result = asyncio.run(planner.create_plan(prompt))

        return jsonify({
            "itinerary": result.get("itinerary", ""),
            "preferences": result.get("preferences", {}),
            "budget_analysis": result.get("budget_analysis", {}),
            "input": {
                "destination": destination,
                "days": days,
                "start_date": start_date,
                "budget": budget,
                "travelers": travelers,
                "travel_style": travel_style,
                "interests": interests,
            }
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# ─── Legacy /chat (for test_end_to_end.py) ────────────────
@app.route("/chat", methods=["POST"])
def chat_legacy():
    data = request.get_json()
    message = data.get("message", "")
    if not message:
        return jsonify({"error": "Message is required"}), 400
    try:
        planner = PlannerAgent()
        response_text = asyncio.run(planner.chat(message))
        return jsonify({"response": response_text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/reset", methods=["POST"])
def reset():
    planners.clear()
    return jsonify({"status": "reset successful"})


if __name__ == "__main__":
    print(f"Starting PlanIT API on {settings.api_host}:{settings.api_port}")
    app.run(host=settings.api_host, port=settings.api_port, debug=settings.debug)
