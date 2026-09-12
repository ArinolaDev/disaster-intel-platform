"""
src/ingestion/weather.py

Pulls historical + forecast rainfall data for known flood-prone locations
in Bangladesh from the Open-Meteo API (free, no API key required).

Phase 1 scope: a handful of hardcoded points to prove the pipeline works.
Phase 2 will replace POINTS with a full geospatial grid over the region.
"""

import requests
import pandas as pd
from pathlib import Path
from datetime import date, timedelta

# --- Known flood-prone locations in Bangladesh ---
# Chosen from the UNOSAT flood exposure dashboard (high-exposure districts)
POINTS = {
    "Sylhet":     {"lat": 24.8949, "lon": 91.8687},
    "Sirajganj":  {"lat": 24.4534, "lon": 89.7000},
    "Bogura":     {"lat": 24.8465, "lon": 89.3773},
    "Cumilla":    {"lat": 23.4607, "lon": 91.1809},
    "Rangpur":    {"lat": 25.7439, "lon": 89.2752},
    "Mymensingh": {"lat": 24.7471, "lon": 90.4203},
}

RAW_DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "raw" / "flood"

HISTORICAL_URL = "https://archive-api.open-meteo.com/v1/archive"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

DAILY_VARS = "precipitation_sum,rain_sum,precipitation_hours"
HOURLY_VARS = "precipitation,rain"


def fetch_historical(lat: float, lon: float, start_date: str, end_date: str) -> pd.DataFrame:
    """Fetch daily historical rainfall for one point between two dates."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "daily": DAILY_VARS,
        "timezone": "Asia/Dhaka",
    }
    resp = requests.get(HISTORICAL_URL, params=params, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    df = pd.DataFrame(data["daily"])
    df["time"] = pd.to_datetime(df["time"])
    return df


def fetch_forecast(lat: float, lon: float, days: int = 7) -> pd.DataFrame:
    """Fetch hourly forecast rainfall for one point, next `days` days."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": HOURLY_VARS,
        "forecast_days": days,
        "timezone": "Asia/Dhaka",
    }
    resp = requests.get(FORECAST_URL, params=params, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    df = pd.DataFrame(data["hourly"])
    df["time"] = pd.to_datetime(df["time"])
    return df


def pull_all_points(start_date: str, end_date: str, file_prefix: str = "historical"):
    """Pull historical rainfall for every point in POINTS and save to CSV."""
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    for name, coords in POINTS.items():
        print(f"Fetching {file_prefix} rainfall for {name} ({start_date} to {end_date})...")
        hist_df = fetch_historical(coords["lat"], coords["lon"], start_date, end_date)
        hist_df["location"] = name
        hist_path = RAW_DATA_DIR / f"{file_prefix}_{name.lower()}.csv"
        hist_df.to_csv(hist_path, index=False)
        print(f"  -> saved {len(hist_df)} rows to {hist_path}")


def pull_forecasts():
    """Pull current 7-day forecast for every point in POINTS and save to CSV."""
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    for name, coords in POINTS.items():
        print(f"Fetching forecast rainfall for {name}...")
        fcst_df = fetch_forecast(coords["lat"], coords["lon"])
        fcst_df["location"] = name
        fcst_path = RAW_DATA_DIR / f"forecast_{name.lower()}.csv"
        fcst_df.to_csv(fcst_path, index=False)
        print(f"  -> saved {len(fcst_df)} rows to {fcst_path}")


if __name__ == "__main__":
    print("Pulling TRAINING-RANGE rainfall (2000-2018, matches flood event labels)...")
    pull_all_points(start_date="2000-01-01", end_date="2018-12-31", file_prefix="training")

    print("\nPulling RECENT rainfall (last 2 years, for live prediction later)...")
    today = date.today()
    end = today - timedelta(days=5)
    start = end - timedelta(days=730)
    pull_all_points(start_date=start.isoformat(), end_date=end.isoformat(), file_prefix="historical")

    print("\nPulling current 7-day forecast...")
    pull_forecasts()

    print("\nDone. Check data/raw/flood/ for output CSVs.")