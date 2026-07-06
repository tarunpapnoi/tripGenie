# --- Tool Definition: A function that calls a live public API ---
import asyncio

import requests
import json

from google.adk import Agent

from TheDayTripGenie.tripagent import run_agent_query, session_service, my_user_id

# A simple lookup to avoid needing a separate geocoding API for this example
LOCATION_COORDINATES = {
    "sunnyvale": "37.3688,-122.0363",
    "san francisco": "37.7749,-122.4194",
    "lake tahoe": "39.0968,-120.0324"
}

def get_live_weather_forecast(location: str) -> dict:
    """Gets the current, real-time weather forecast for a specified location in the US.

    Args:
        location: The city name, e.g., "San Francisco".

    Returns:
        A dictionary containing the temperature and a detailed forecast.
    """
    print(f"🛠️ TOOL CALLED: get_live_weather_forecast(location='{location}')")

    # Find coordinates for the location
    normalized_location = location.lower()
    coords_str = None
    for key, val in LOCATION_COORDINATES.items():
        if key in normalized_location:
            coords_str = val
            break
    if not coords_str:
        return {"status": "error", "message": f"I don't have coordinates for {location}."}

    try:
        # NWS API requires 2 steps: 1. Get the forecast URL from the coordinates.
        points_url = f"https://api.weather.gov/points/{coords_str}"
        headers = {"User-Agent": "ADK Example Notebook"}
        points_response = requests.get(points_url, headers=headers)
        points_response.raise_for_status() # Raise an exception for bad status codes
        forecast_url = points_response.json()['properties']['forecast']

        # 2. Get the actual forecast from the URL.
        forecast_response = requests.get(forecast_url, headers=headers)
        forecast_response.raise_for_status()

        # Extract the relevant forecast details
        current_period = forecast_response.json()['properties']['periods'][0]
        return {
            "status": "success",
            "temperature": f"{current_period['temperature']}°{current_period['temperatureUnit']}",
            "forecast": current_period['detailedForecast']
        }
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"API request failed: {e}"}

# --- Agent Definition: An agent that USES the new tool ---

weather_agent = Agent(
    name="weather_aware_planner",
    model="gemini-2.5-flash",
    description="A trip planner that checks the real-time weather before making suggestions.",
    instruction="You are a cautious trip planner. Before suggesting any outdoor activities, you MUST use the `get_live_weather_forecast` tool to check conditions. Incorporate the live weather details into your recommendation.",
    tools=[get_live_weather_forecast]
)

print(f"🌦️ Agent '{weather_agent.name}' is created and can now call a live weather API!")

# --- Let's test the Weather-Aware Planner ---

async def run_weather_planner_test():
    weather_session = await session_service.create_session(app_name=weather_agent.name, user_id=my_user_id)
    query = "I want to go hiking near Lake Tahoe, what's the weather like?"
    print(f"🗣️ User Query: '{query}'")
    await run_agent_query(weather_agent, query, weather_session, my_user_id)


asyncio.run(run_weather_planner_test())