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
