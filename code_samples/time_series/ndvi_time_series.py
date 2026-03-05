"""
Task type: time_series
Description: Compute NDVI (Normalized Difference Vegetation Index) per timestep from multi-band rasters.
Use case: Vegetation health monitoring over time using NIR and Red bands.
Input: /workspace/input/data.json with STAC items containing multi-band raster assets.
Output: /workspace/output/ndvi_time_series.png — line chart of mean NDVI over time.
         /workspace/output/ndvi_time_series.csv — table of datetime vs mean NDVI.
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
    for key, info in assets.items():
        href = info.get("href", "")
        if href and not href.endswith((".xml", ".json")):
            return href
    return None


def compute_ndvi(red: np.ndarray, nir: np.ndarray) -> np.ndarray:
    """Compute NDVI = (NIR - Red) / (NIR + Red), with NaN for zero-denominator."""
    red = red.astype(float)
    nir = nir.astype(float)
    denom = nir + red
    with np.errstate(invalid="ignore", divide="ignore"):
        ndvi = np.where(denom == 0, np.nan, (nir - red) / denom)
    return ndvi


# --- Main ---------------------------------------------------------------------

with open("/workspace/input/data.json") as f:
    data = json.load(f)

items = data.get("items", [])
print(f"Processing {len(items)} items for NDVI...")

records = []
for item in items:
    href = get_raster_asset(item["assets"])
    if not href:
        print(f"  Skipping {item['id']} — no raster asset found")
        continue

    try:
        with rasterio.open(href) as src:
            band_count = src.count
            if band_count >= 2:
                # Assume band 1 = Red, band 2 = NIR (common for MODIS/Sentinel products)
                red = src.read(1).astype(float)
                nir = src.read(2).astype(float)
                nodata = src.nodata
                if nodata is not None:
                    red = np.where(red == nodata, np.nan, red)
                    nir = np.where(nir == nodata, np.nan, nir)
                ndvi = compute_ndvi(red, nir)
            else:
                # Single-band fallback: treat as pre-computed NDVI or index
                arr = src.read(1).astype(float)
                nodata = src.nodata
                if nodata is not None:
                    arr = np.where(arr == nodata, np.nan, arr)
                ndvi = arr

            mean_ndvi = float(np.nanmean(ndvi))

        records.append({"datetime": item["datetime"], "mean_ndvi": mean_ndvi})
        print(f"  {item['id']}: mean NDVI = {mean_ndvi:.4f}")
    except Exception as e:
        print(f"  Skipping {item['id']} — error: {e}")

if not records:
    with open("/workspace/output/no_data.txt", "w") as f:
        f.write("No renderable raster assets were found in the provided items.")
    print("No data to plot.")
else:
    df = pd.DataFrame(records)
    df["datetime"] = pd.to_datetime(df["datetime"])
    df = df.sort_values("datetime")

    df.to_csv("/workspace/output/ndvi_time_series.csv", index=False)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["datetime"], df["mean_ndvi"], marker="o", linewidth=2, color="green", markersize=5)
    ax.axhline(0, color="black", linewidth=0.8, linestyle="--", alpha=0.5)
    ax.set_ylim(-1, 1)
    ax.set_title(f"NDVI Time Series — {data.get('user_query', 'Vegetation Analysis')}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Mean NDVI")
    ax.grid(True, alpha=0.3)
    fig.autofmt_xdate()
    plt.tight_layout()
    plt.savefig("/workspace/output/ndvi_time_series.png", dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved ndvi_time_series.png and ndvi_time_series.csv ({len(df)} data points)")
