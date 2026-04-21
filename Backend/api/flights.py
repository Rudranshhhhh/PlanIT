import os
import requests
import asyncio
from config import settings

def get_iata_codes(origin: str, destination: str) -> dict:
    """Uses Groq to reliably get the exact 3-letter IATA codes."""
    if not settings.groq_api_key:
        return {"origin_iata": None, "destination_iata": None}

    headers = {
        "Authorization": f"Bearer {settings.groq_api_key}",
        "Content-Type": "application/json"
    }

    prompt = f"""You are an airline API helper. Convert the following cities to their 3-letter IATA airport codes.
Origin City: {origin}
Destination City: {destination}
Return strictly a JSON object with keys "origin_iata" and "destination_iata" without any markdown wrappers or explanation. Example: {{"origin_iata": "JFK", "destination_iata": "LHR"}}"""

    data = {
        "model": settings.groq_model or "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.0,
        "response_format": {"type": "json_object"}
    }

    try:
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=data, timeout=8)
        if response.status_code == 200:
            res_data = response.json()
            content = res_data["choices"][0]["message"]["content"]
            import json
            parsed = json.loads(content)
            return parsed
    except Exception as e:
        print(f"Error fetching IATA: {e}")
    return {"origin_iata": None, "destination_iata": None}


def fetch_flight_prices(origin_iata: str, dest_iata: str, depart_date: str) -> list:
    """Fetches cheap flights from Travelpayouts and builds affiliate URLs, returning up to 4 options."""
    if not settings.travelpayouts_api_key or not origin_iata or not dest_iata:
        return []

    url = f"https://api.travelpayouts.com/v1/prices/cheap"
    params = {
        "origin": origin_iata,
        "destination": dest_iata,
        "currency": "INR",
        "token": settings.travelpayouts_api_key
    }

    try:
        resp = requests.get(url, params=params, timeout=8)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success") and dest_iata in data["data"]:
                flights = data["data"][dest_iata]
                
                # flights is a dict {'0': {price, etc}, '1': {price, etc}}
                flight_list = list(flights.values())
                
                # Sort by price ascending
                flight_list.sort(key=lambda x: x.get("price", 999999))
                
                # Take top 4 cheapest
                top_flights = flight_list[:4]
                
                result_flights = []
                marker = settings.travelpayouts_marker or "721282"
                
                for fl in top_flights:
                    departStr = datetime_to_ddmm(fl.get("departure_at", depart_date))
                    booking_url = f"https://search.aviasales.com/flights/{origin_iata}{departStr}{dest_iata}1?marker={marker}"
                    
                    result_flights.append({
                        "origin_iata": origin_iata,
                        "destination_iata": dest_iata,
                        "price_inr": fl.get("price"),
                        "airline": fl.get("airline"),
                        "flight_number": fl.get("flight_number"),
                        "departure_at": fl.get("departure_at"),
                        "booking_url": booking_url
                    })
                    
                return result_flights
    except Exception as e:
        print(f"Error fetching flights: {e}")

    return []


def datetime_to_ddmm(datetime_str: str) -> str:
    """Convert '2026-04-25T10:00:00Z' to '2504' for the aviasales booking link."""
    # format of datetime_str is 'YYYY-MM-DD...'
    if len(datetime_str) >= 10:
        parts = datetime_str[:10].split("-")
        if len(parts) == 3:
            return f"{parts[2]}{parts[1]}"
    return ""

