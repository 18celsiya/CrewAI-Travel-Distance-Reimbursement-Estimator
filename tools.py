#==============================================
# Import necessary libraries
#===============================================

import os # for environment variables
import requests # for making API calls to GraphHopper
from crewai.tools import tool # for defining tools
from dotenv import load_dotenv # for loading environment variables from .env file

# Load environment variables from .env file
load_dotenv()

# GraphHopper API key for distance calculations
GRAPHOPPER_API_KEY = os.getenv("GRAPHHOPPER_API_KEY")

#==============================================
# Tool: Get City Distance
#==============================================

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
        # Geocode addresses
        # ----------------------------
        def geocode(address):
            url = "https://graphhopper.com/api/1/geocode"
            params = {
                "q": address,
                "limit": 1,
                "locale": "en",
                "key": GRAPHOPPER_API_KEY
            }
            # Make the geocoding request
            resp = requests.get(url, params=params)
            data = resp.json()
            if "hits" in data and len(data["hits"]) > 0:
                # Extract latitude and longitude from the first hit
                lat = data["hits"][0]["point"]["lat"]
                lng = data["hits"][0]["point"]["lng"]
                return f"{lat},{lng}"
            else:
                raise ValueError(f"Geocoding failed for address: {address}")
        
        # Get coordinates for both addresses
        origin = geocode(starting_address)
        destination = geocode(destination_address)

        # ----------------------------
        #  Request route
        # ----------------------------
        # GraphHopper routing API endpoint and parameters
        route_url = "https://graphhopper.com/api/1/route"
        route_params = {
            "point": [origin, destination],
            "profile": mode_of_transport,
            "calc_points": "false",
            "weighting": "fastest",  # match GraphHopper Map UI
            "key": GRAPHOPPER_API_KEY
        }
        
        # Make the routing request
        route_resp = requests.get(route_url, params=route_params)
        route_data = route_resp.json()

        # ----------------------------
        #  Extract distance in meters
        # ----------------------------
        if "paths" in route_data and len(route_data["paths"]) > 0:
            # Extract distance from the first path
            distance_meters = route_data["paths"][0]["distance"]
            return distance_meters
        else:
            print(f"No route found for: {starting_address} → {destination_address}")
            return None

    except Exception as e:
        print("Distance calculation error:", e)
        return None