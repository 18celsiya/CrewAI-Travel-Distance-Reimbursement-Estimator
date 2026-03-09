# tools.py
import os
from crewai.tools import tool
from graphh import GraphHopper
from dotenv import load_dotenv

load_dotenv()

# Initialize GraphHopper client with your API key
mapper = GraphHopper(api_key=os.getenv("GRAPHHOPPER_API_KEY"))

@tool("get_city_distance_okay")
def get_city_distance(
    starting_address: str,
    destination_address: str,
    mode_of_transport: str = "car"  # car, bike, foot
):
    """
    Returns the raw distance in meters between two addresses using GraphHopper API.
    """
    try:
        origin = mapper.address_to_latlong(starting_address)
        destination = mapper.address_to_latlong(destination_address)

        if not origin or not destination:
            print(f"Geocoding failed for: {starting_address} → {destination_address}")
            return "Distance not found"

        route_data = mapper.route([origin, destination], vehicle=mode_of_transport)

        if 'paths' not in route_data or len(route_data['paths']) == 0:
            print(f"No route found for: {starting_address} → {destination_address}")
            return "Distance not found"

        distance_meters = route_data['paths'][0]['distance']
        return distance_meters

    except Exception as e:
        print("Distance calculation error:", e)
        return "Distance not found"