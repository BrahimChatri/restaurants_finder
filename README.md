
# Restaurant Rating Finder

This Python script fetches restaurant data within a specified city and filters out restaurants with ratings below given rate using the Google Places API. The data is saved in both CSV and JSON formats for easy access and analysis.

## Features

- **Grid-based Search**: The city is divided into 5KM x 5KM grid sections to ensure thorough coverage.
- **Rating Filter**: Filters restaurants with a rating lower than 2.5 stars.
- **Data Saving**: Saves both the full list of restaurants and the low-rated restaurants to CSV and JSON files.
- **Flexible Configuration**: Easily change the city center, grid size, and rating threshold.

## Requirements

- Python 3.x
- `requests` library
- `python-dotenv` library (for managing environment variables)
- A valid **Google Places API key**

## Setup

### 1. Clone the Repository

```bash
git clone git@github.com:BrahimChatri/restaurants_finder.git
cd restaurants_finder
```

### 2. Install Dependencies

Install the required libraries using `pip`:

```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables

Create a `.env` file in the root directory and add your Google Places API key:

```env
API_KEY=your_google_places_api_key
```

You can obtain an API key from the [Google Cloud Console](https://console.cloud.google.com/).

### 4. Customize the City and Grid Parameters

In the script, you can modify the following parameters:

- `CITY_CENTER_LAT` and `CITY_CENTER_LNG`: Latitude and longitude of the city center. Change these to your desired location.
- `GRID_SIZE_KM`: The size of each grid cell in kilometers (default is 5KM x 5KM).
- `MAX_RESULTS`: The maximum number of restaurants to fetch (default is 1000).

### 5. Run the Script

To run the script, simply execute the following command:

```bash
python main.py
```

The script will begin fetching restaurant data and save the results into CSV and JSON files.

## Output Files

The script generates the following files:

- **all_restaurants.csv**: Contains data for all fetched restaurants.
- **all_restaurants.json**: Contains data for all fetched restaurants in JSON format.
- **low_rated_restaurants.csv**: Contains data for low-rated restaurants in csv format.
- **low_rated_restaurants.json**: Contains data for low-rated restaurants in JSON format.

All files are saved in the `data/` folder.

## Example Data

The saved data includes the following fields:

- `Name`: The name of the restaurant.
- `Rating`: The rating of the restaurant.
- `Address`: The address of the restaurant.
- `URL`: A link to the restaurant on Google Maps.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- The script uses the [Google Places API](https://developers.google.com/maps/documentation/places/web-service/overview) to fetch restaurant data check their docs. 