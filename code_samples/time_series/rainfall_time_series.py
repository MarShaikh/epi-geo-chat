"""
Task type: time_series
Description: Compute mean pixel value per timestep from a set of raster items and plot a line chart.
Use case: Rainfall, precipitation, or any single-band quantity over time.
Input: /workspace/input/data.json with STAC items containing raster assets.
Output: /workspace/output/time_series.png — line chart of mean value over time.
         /workspace/output/time_series.csv — table of datetime vs mean value.
"""

import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import rasterio

# --- Helper -------------------------------------------------------------------

def get_raster_asset(assets):
    """Find the first renderable raster asset from an item's assets dict."""
    RASTER_TYPES = {
        "image/tiff",
        "image/tiff; application=geotiff",
        "image/vnd.stac.geotiff",
        "application/x-geotiff",
    }
    for key, info in assets.items():
        if info.get("type", "") in RASTER_TYPES:
            return info["href"]
    # Fallback: first asset with an href that isn't metadata
    for key, info in assets.items():
        href = info.get("href", "")
        if href and not href.endswith((".xml", ".json")):
            return href
    return None


# --- Main ---------------------------------------------------------------------

with open("/workspace/input/data.json") as f:
    data = json.load(f)

items = data.get("items", [])
print(f"Processing {len(items)} items...")

records = []
for item in items:
    href = get_raster_asset(item["assets"])
    if not href:
        print(f"  Skipping {item['id']} — no raster asset found")
        continue

    try:
        with rasterio.open(href) as src:
            arr = src.read(1).astype(float)
            nodata = src.nodata
            if nodata is not None:
                arr = np.where(arr == nodata, np.nan, arr)
            mean_val = float(np.nanmean(arr))
        records.append({"datetime": item["datetime"], "mean_value": mean_val})
        print(f"  {item['id']}: mean = {mean_val:.4f}")
    except Exception as e:
        print(f"  Skipping {item['id']} — error reading raster: {e}")

if not records:
    with open("/workspace/output/no_data.txt", "w") as f:
        f.write("No renderable raster assets were found in the provided items.")
    print("No data to plot.")
else:
    df = pd.DataFrame(records)
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.sort_values("datetime")

    # Save CSV
    df.to_csv("/workspace/output/time_series.csv", index=False)

    # Plot
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["datetime"], df["mean_value"], marker="o", linewidth=2, markersize=5)
    ax.set_title(f"Time Series — {data.get('user_query', 'Analysis')}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Mean Value")
    ax.grid(True, alpha=0.3)
    fig.autofmt_xdate()
    plt.tight_layout()
    plt.savefig("/workspace/output/time_series.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved time_series.png and time_series.csv ({len(df)} data points)")
