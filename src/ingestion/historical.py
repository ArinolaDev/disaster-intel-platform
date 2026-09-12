import ee
import pandas as pd
from pathlib import Path

ee.Initialize(project="disaster-intel-platform")

POINTS = {
    "Sylhet":     {"lat": 24.8949, "lon": 91.8687},
    "Sirajganj":  {"lat": 24.4534, "lon": 89.7000},
    "Bogura":     {"lat": 24.8465, "lon": 89.3773},
    "Cumilla":    {"lat": 23.4607, "lon": 91.1809},
    "Rangpur":    {"lat": 25.7439, "lon": 89.2752},
    "Mymensingh": {"lat": 24.7471, "lon": 90.4203},
}

RAW_DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "raw" / "flood"

GFD_COLLECTION = "GLOBAL_FLOOD_DB/MODIS_EVENTS/V1"
BUFFER_METERS = 15000


def get_flood_events_for_point(lat: float, lon: float, name: str) -> pd.DataFrame:
    point = ee.Geometry.Point([lon, lat])
    region = point.buffer(BUFFER_METERS)

    collection = ee.ImageCollection(GFD_COLLECTION).filterBounds(region)

    def check_flood(image):
        flooded_img = ee.Image(image).select(["flooded"])
        sample = flooded_img.reduceRegion(
            reducer=ee.Reducer.max(),
            geometry=region,
            scale=250,
            maxPixels=1e9,
            bestEffort=True,
            tileScale=4,
        )
        flooded_val = ee.Algorithms.If(
            sample.contains("flooded"),
            sample.get("flooded"),
            0,
        )
        return image.set("was_flooded_here", flooded_val)

    tagged = collection.map(check_flood)
    flooded_here = tagged.filter(ee.Filter.gt("was_flooded_here", 0))

    event_list = flooded_here.toList(flooded_here.size())
    n_events = event_list.size().getInfo()

    rows = []
    for i in range(n_events):
        img = ee.Image(event_list.get(i))
        rows.append({
            "location": name,
            "system_index": img.get("system:index").getInfo(),
            "start_time": pd.to_datetime(img.get("system:time_start").getInfo(), unit="ms"),
            "end_time": pd.to_datetime(img.get("system:time_end").getInfo(), unit="ms"),
            "dfo_country": img.get("cc").getInfo(),
            "dfo_severity": img.get("dfo_severity").getInfo(),
            "dfo_main_cause": img.get("dfo_main_cause").getInfo(),
        })

    return pd.DataFrame(rows)


def pull_all_points():
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    all_events = []

    for name, coords in POINTS.items():
        print(f"Querying Global Flood Database near {name}...")
        df = get_flood_events_for_point(coords["lat"], coords["lon"], name)
        print(f"  -> found {len(df)} historical flood events")
        all_events.append(df)

    combined = pd.concat(all_events, ignore_index=True)
    out_path = RAW_DATA_DIR / "historical_flood_events.csv"
    combined.to_csv(out_path, index=False)
    print(f"\nSaved {len(combined)} total flood event records to {out_path}")
    return combined


if __name__ == "__main__":
    pull_all_points()