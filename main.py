import requests
import time
import json
import csv
import os
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("API_KEY")

# Central Location (Taipei) - Change for different cities
CITY_CENTER_LAT = 25.0330
CITY_CENTER_LNG = 121.5654
SEARCH_RADIUS = 5000  # Bigger radius to capture more restaurants
GRID_SPACING = 0.05  # Adjust for better city coverage
MAX_RESULTS = 10000  # Target up to 10,000 restaurants
LOW_RATING_THRESHOLD = 2.6  # Only save restaurants with rating ≤ 2.6


def get_restaurants(api_key, lat, lng, radius=5000):
    """Fetches restaurants in a given area using Google Places API."""
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": radius,
        "type": "restaurant",
        "key": api_key
    }

    low_rated_restaurants = {}  # Dictionary to store unique low-rated restaurants

    while len(low_rated_restaurants) < MAX_RESULTS:
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if "results" in data:
                for r in data["results"]:
                    place_id = r.get("place_id")
                    rating = r.get("rating", 5.0)  # Default to 5 if no rating

                    # Filter low-rated restaurants (rating ≤ 2.6)
                    if place_id and place_id not in low_rated_restaurants and rating <= LOW_RATING_THRESHOLD:
                        low_rated_restaurants[place_id] = {
                            "name": r.get("name", "Unknown"),
                            "rating": rating,
                            "address": r.get("vicinity", "N/A"),
                            "url": f"https://www.google.com/maps/place/?q=place_id:{place_id}"
                        }

            if "next_page_token" in data:
                params["pagetoken"] = data["next_page_token"]
                time.sleep(2)  # Google requires a delay before using next_page_token
            else:
                break
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            time.sleep(5)  # Retry after 5 seconds if there's a network issue

    return list(low_rated_restaurants.values())  # Return only low-rated restaurants


def generate_grid(center_lat, center_lng, spacing, num_points=8):
    """Generates a grid of search points around a central location."""
    latitudes = [center_lat + (i - num_points//2) * spacing for i in range(num_points)]
    longitudes = [center_lng + (i - num_points//2) * spacing for i in range(num_points)]
    
    grid_points = [(lat, lng) for lat in latitudes for lng in longitudes]
    return grid_points


def save_to_csv(restaurants, filename):
    """Saves restaurant data to a CSV file."""
    os.makedirs("data", exist_ok=True)
    file_path = os.path.join("data", filename)

    with open(file_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Rating", "Address", "Google Maps URL"])

        for r in restaurants:
            writer.writerow([r["name"], r["rating"], r["address"], r["url"]])

    print(f"✅ Data saved to {filename}")


def save_to_json(data, filename):
    """Saves the restaurant data to a JSON file."""
    os.makedirs("data", exist_ok=True)
    file_path = os.path.join("data", filename)

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print(f"✅ Data saved to {filename}")


def main():
    """Main function to fetch and save restaurant data."""
    print("🔍 Searching for low-rated restaurants in multiple locations...")

    grid_points = generate_grid(CITY_CENTER_LAT, CITY_CENTER_LNG, GRID_SPACING, num_points=8)
    
    all_restaurants = {}  # Store unique low-rated restaurants

    for lat, lng in grid_points:
        print(f"📍 Searching in area: {lat}, {lng}")
        restaurants = get_restaurants(API_KEY, lat, lng, SEARCH_RADIUS)

        for r in restaurants:
            all_restaurants[r["url"]] = r  # Avoid duplicates using URL as a unique key

        print(f"📊 Total low-rated restaurants found so far: {len(all_restaurants)}")

        if len(all_restaurants) >= MAX_RESULTS:
            break  # Stop if we reach the limit

    final_restaurants = list(all_restaurants.values())

    save_to_json(final_restaurants, filename="low_rated.json")
    save_to_csv(final_restaurants, filename="low_rated.csv")


if __name__ == "__main__":
    main()
