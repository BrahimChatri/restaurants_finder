import requests
import time, json
import csv
import os
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
API_KEY = os.getenv("API_KEY")

# Taipei city boundaries (change for another city)
CITY_CENTER_LAT = 25.0330 
CITY_CENTER_LNG = 121.5654
GRID_SIZE_KM = 5  # Each grid covers 5KM x 5KM
MAX_RESULTS = 1000  # Target number of restaurants

# Earth constants for distance calculation
KM_IN_DEGREES = 1 / 111  # 1 degree latitude = ~111KM


def get_restaurants(api_key, lat, lng, radius=5000):
    """Fetch restaurants within a given 5KM radius using Google Places API."""
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    params = {
        "location": f"{lat},{lng}",
        "radius": radius,
        "type": "restaurant",
        "key": api_key
    }

    restaurants = []
    while len(restaurants) < MAX_RESULTS:
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            if "results" in data:
                restaurants.extend(data["results"])

            if "next_page_token" in data:
                params["pagetoken"] = data["next_page_token"]
                time.sleep(1.5)  # Google requires a delay before using next_page_token
            else:
                break
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            time.sleep(5)  # Retry after 5 seconds in case of a network issue
        else:
            if len(restaurants) >= MAX_RESULTS:
                break  # Stop once we reach MAX_RESULTS

    return restaurants


def generate_grid(center_lat, center_lng, grid_size_km, num_cells=3):
    """Generates grid coordinates to cover the city using 5KM x 5KM squares."""
    grid = []
    step = grid_size_km * KM_IN_DEGREES  # Convert KM to degrees

    for i in range(-num_cells, num_cells + 1):
        for j in range(-num_cells, num_cells + 1):
            lat = center_lat + (i * step)
            lng = center_lng + (j * step)
            grid.append((lat, lng))

    return grid


def save_to_csv(restaurants, filename="restaurants.csv"):
    """Saves restaurant data to a CSV file."""
    file_path = os.path.join(os.path.dirname(__file__), "data", filename)
    with open(file_path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Rating", "Google Maps URL"])

        for r in restaurants:
            name = r.get("name", "Unknown")
            rating = r.get("rating", "N/A")
            place_id = r.get("place_id", "")
            google_maps_url = f"https://www.google.com/maps/place/?q=place_id:{place_id}" if place_id else "N/A"

            writer.writerow([name, rating, google_maps_url])

    print(f"✅ Data saved to {filename}")

def save_to_json(user_data: dict, filename) -> None:
    """Save the user data to the JSON file."""
    file_path = os.path.join(os.path.dirname(__file__), "data", filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(user_data, f, indent=4)
    
    print(f"Saved {len(user_data)} restaurants to {filename}")

def filter_low_rated(restaurants, max_rating=2.5):
    """Filters restaurants with ratings below the specified max_rating."""
    return [
        {
            "name": r.get("name", "Unknown"),
            "rating": r.get("rating", "N/A"),
            "address": r.get("vicinity", "N/A"),
            "url": f"https://www.google.com/maps/place/?q=place_id:{r.get('place_id', '')}"
        }
        for r in restaurants if "rating" in r and r["rating"] <= max_rating
    ]

def main():
    """Main function to fetch restaurants using a grid-based search."""
    grid_points = generate_grid(CITY_CENTER_LAT, CITY_CENTER_LNG, GRID_SIZE_KM)
    all_restaurants = []

    print(f"🔍 Searching in {len(grid_points)} grid sections...")

    for idx, (lat, lng) in enumerate(grid_points):
        print(f"📍 Searching area {idx + 1}/{len(grid_points)} at ({lat}, {lng})...")
        restaurants = get_restaurants(API_KEY, lat, lng, radius=15000)

        for r in restaurants:
            name = r.get("name", "Unknown")
            rating = r.get("rating", "N/A")
            print(f"   - {name} (⭐ {rating})")

        all_restaurants.extend(restaurants)

        if len(all_restaurants) >= MAX_RESULTS:
            break  # Stop once we reach 500 restaurants

    save_to_json(all_restaurants, filename="all_restaurants.json")
    save_to_csv(all_restaurants, filename="all_restaurants.csv")

    low_rated = filter_low_rated(all_restaurants, max_rating=2.6)
    save_to_csv(low_rated, filename="low_rated_restaurants.csv")
    save_to_json(low_rated, filename="low_rated_restaurants.json")


if __name__ == "__main__":
    main()
