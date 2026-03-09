import os
import requests
from crewai.tools import tool
from dotenv import load_dotenv

load_dotenv()

GRAPHOPPER_API_KEY = os.getenv("GRAPHHOPPER_API_KEY")

@tool("get_city_distance")
def get_city_distance(
    starting_address: str,
    destination_address: str,
    mode_of_transport: str = "car"  # car, bike, foot
):
    """
    Returns the distance in meters between two addresses using GraphHopper REST API.
    """
    try:
        # ----------------------------
        # Step 1: Geocode addresses
        # ----------------------------
        def geocode(address):
            url = "https://graphhopper.com/api/1/geocode"
            params = {
                "q": address,
                "limit": 1,
                "locale": "en",
                "key": GRAPHOPPER_API_KEY
            }
            resp = requests.get(url, params=params)
            data = resp.json()
            if "hits" in data and len(data["hits"]) > 0:
                lat = data["hits"][0]["point"]["lat"]
                lng = data["hits"][0]["point"]["lng"]
                return f"{lat},{lng}"
            else:
                raise ValueError(f"Geocoding failed for address: {address}")

        origin = geocode(starting_address)
        destination = geocode(destination_address)

        # ----------------------------
        # Step 2: Request route
        # ----------------------------
        route_url = "https://graphhopper.com/api/1/route"
        route_params = {
            "point": [origin, destination],
            "profile": mode_of_transport,
            "calc_points": "false",
            "weighting": "fastest",  # match GraphHopper Map UI
            "key": GRAPHOPPER_API_KEY
        }

        route_resp = requests.get(route_url, params=route_params)
        route_data = route_resp.json()

        # ----------------------------
        # Step 3: Extract distance in meters
        # ----------------------------
        if "paths" in route_data and len(route_data["paths"]) > 0:
            distance_meters = route_data["paths"][0]["distance"]
            return distance_meters
        else:
            print(f"No route found for: {starting_address} → {destination_address}")
            return None

    except Exception as e:
        print("Distance calculation error:", e)
        return None