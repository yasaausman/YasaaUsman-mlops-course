"""
Week 3 Lab — Starter Script (uninstrumented)

Fetches the current weather for a single hardcoded city from the free
Open-Meteo API (https://open-meteo.com) — no API key or signup required.

This version is intentionally fragile: no timeout, no status check, no
error handling, no retry logic, and it doesn't save (land) the raw
response anywhere. Run it once as-is to see the happy path, then build
all of that up yourself — that's today's lab.
"""
import os
import json
import time
from datetime import datetime

import requests

CITY_NAME = "Seattle"
LATITUDE = 47.6062
LONGITUDE = -122.3321

MAX_RETRIES = 4
BASE_DELAY = 1  # seconds

RAW_DATA_DIR = "data/raw"


def save_raw_response(payload, city_name):
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{city_name.lower()}_{timestamp}.json"
    path = os.path.join(RAW_DATA_DIR, filename)
    with open(path, "w") as f:
        json.dump(payload, f, indent=2)
    return path


def fetch_current_weather(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,wind_speed_10m,relative_humidity_2m",
        "timezone": "auto",
    }
    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()   # don't silently swallow a bad response
        return response.json()
    except requests.exceptions.Timeout:
        print("Request timed out.")
        return None
    except requests.exceptions.ConnectionError:
        print("Could not connect to the API.")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"API returned an error: {e}")
        return None


def fetch_with_retry(lat, lon):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,wind_speed_10m,relative_humidity_2m",
        "timezone": "auto",
    }
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            return response.json()
        except (requests.exceptions.Timeout,
                requests.exceptions.ConnectionError) as e:
            if attempt == MAX_RETRIES:
                print(f"Giving up after {MAX_RETRIES} attempts: {e}")
                return None
            delay = BASE_DELAY * (2 ** (attempt - 1))
            print(f"Attempt {attempt} failed ({type(e).__name__}). Retrying in {delay}s...")
            time.sleep(delay)
        except requests.exceptions.HTTPError as e:
            print(f"Request rejected by the API, not retrying: {e}")
            return None


CITIES = {
    "Seattle": (47.6062, -122.3321),
    "New York": (40.7128, -74.0060),
    "Austin": (30.2672, -97.7431),
}


def ingest_weather():
    for city_name, (lat, lon) in CITIES.items():
        payload = fetch_with_retry(lat, lon)
        if payload is None:
            print(f"Skipping {city_name} — no data ingested this run.")
            continue
        path = save_raw_response(payload, city_name)
        print(f"Landed {city_name} weather at {path}")


if __name__ == "__main__":
    ingest_weather()
