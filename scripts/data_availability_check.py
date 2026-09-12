import pandas as pd
from pathlib import Path

RAW_DIR = Path(__file__).resolve().parents[1] / "data" / "raw" / "flood"

LOCATIONS = ["sylhet", "sirajganj", "bogura", "cumilla", "rangpur", "mymensingh"]


def check_rainfall_data():
    print("=" * 60)
    print("RAINFALL DATA (Open-Meteo) — TRAINING RANGE")
    print("=" * 60)
    for loc in LOCATIONS:
        hist_path = RAW_DIR / f"training_{loc}.csv"
        df = pd.read_csv(hist_path, parse_dates=["time"])
        n_missing = df["precipitation_sum"].isna().sum()
        print(f"{loc.title():12} | {df['time'].min().date()} to {df['time'].max().date()} "
              f"| {len(df)} days | {n_missing} missing precipitation values")


def check_flood_event_data():
    print()
    print("=" * 60)
    print("FLOOD EVENT DATA (Earth Engine Global Flood Database)")
    print("=" * 60)
    events_path = RAW_DIR / "historical_flood_events.csv"
    df = pd.read_csv(events_path, parse_dates=["start_time", "end_time"])

    print(f"Total events: {len(df)}")
    print(f"Date range: {df['start_time'].min().date()} to {df['end_time'].max().date()}")
    print()
    print("Events per location:")
    print(df["location"].value_counts().to_string())
    print()
    print("Missing severity/cause values:")
    print(f"  dfo_severity missing: {df['dfo_severity'].isna().sum()} / {len(df)}")
    print(f"  dfo_main_cause missing: {df['dfo_main_cause'].isna().sum()} / {len(df)}")


def check_overlap():
    print()
    print("=" * 60)
    print("OVERLAP CHECK — do the two datasets cover the same time period?")
    print("=" * 60)

    rainfall_starts = []
    rainfall_ends = []
    for loc in LOCATIONS:
        df = pd.read_csv(RAW_DIR / f"training_{loc}.csv", parse_dates=["time"])
        rainfall_starts.append(df["time"].min())
        rainfall_ends.append(df["time"].max())

    rainfall_start = min(rainfall_starts)
    rainfall_end = max(rainfall_ends)

    events_df = pd.read_csv(RAW_DIR / "historical_flood_events.csv", parse_dates=["start_time", "end_time"])
    events_start = events_df["start_time"].min()
    events_end = events_df["end_time"].max()

    print(f"Rainfall data covers:    {rainfall_start.date()} to {rainfall_end.date()}")
    print(f"Flood event data covers: {events_start.date()} to {events_end.date()}")

    overlap_start = max(rainfall_start, events_start)
    overlap_end = min(rainfall_end, events_end)

    if overlap_start <= overlap_end:
        print(f"\nOverlapping window: {overlap_start.date()} to {overlap_end.date()}")
        events_in_overlap = events_df[
            (events_df["start_time"] >= overlap_start) & (events_df["end_time"] <= overlap_end)
        ]
        print(f"Flood events falling inside the overlap: {len(events_in_overlap)} / {len(events_df)}")
    else:
        print("\nWARNING: No overlap between rainfall and flood event date ranges.")
        print("This means we cannot directly train a model on matched features + labels")
        print("without pulling additional historical rainfall data further back in time.")


if __name__ == "__main__":
    check_rainfall_data()
    check_flood_event_data()
    check_overlap()