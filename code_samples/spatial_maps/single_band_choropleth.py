"""
Task type: spatial_map
Description: Read a single-band raster, clip to the bounding box, and render a choropleth map.
Use case: Displaying spatial distribution of any gridded variable (rainfall, temperature, elevation).
Input: /workspace/input/data.json with at least one raster item and a bbox field.
Output: /workspace/output/spatial_map.png — choropleth map with colorbar and bounding box overlay.
"""

import json

import matplotlib.pyplot as plt
import numpy as np
import rasterio
from rasterio.windows import from_bounds

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


# --- Main ---------------------------------------------------------------------

with open("/workspace/input/data.json") as f:
    data = json.load(f)

items = data.get("items", [])
bbox = data.get("bbox")  # [min_lon, min_lat, max_lon, max_lat]
user_query = data.get("user_query", "Spatial Map")

# Use the most recent item
item = None
for candidate in reversed(items):
    href = get_raster_asset(candidate["assets"])
    if href:
        item = candidate
        break

if item is None:
    with open("/workspace/output/no_data.txt", "w") as f:
        f.write("No renderable raster assets were found in the provided items.")
    print("No data to render.")
else:
    href = get_raster_asset(item["assets"])
    print(f"Reading raster for item {item['id']}...")

    try:
        with rasterio.open(href) as src:
            if bbox:
                window = from_bounds(bbox[0], bbox[1], bbox[2], bbox[3], src.transform)
                arr = src.read(1, window=window).astype(float)
                extent = [bbox[0], bbox[2], bbox[1], bbox[3]]  # left, right, bottom, top
            else:
                arr = src.read(1).astype(float)
                bounds = src.bounds
                extent = [bounds.left, bounds.right, bounds.bottom, bounds.top]

            nodata = src.nodata
            if nodata is not None:
                arr = np.where(arr == nodata, np.nan, arr)

        # Remove extreme outliers for better visualisation (1st–99th percentile)
        vmin = float(np.nanpercentile(arr, 1))
        vmax = float(np.nanpercentile(arr, 99))

        fig, ax = plt.subplots(figsize=(10, 8))
        im = ax.imshow(
            arr,
            extent=extent,
            cmap="viridis",
            vmin=vmin,
            vmax=vmax,
            origin="upper",
            aspect="equal",
        )
        plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04, label="Value")
        ax.set_title(f"{user_query}\n{item.get('datetime', '')}")
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        plt.tight_layout()
        plt.savefig("/workspace/output/spatial_map.png", dpi=150, bbox_inches="tight")
        plt.close()
        print(f"Saved spatial_map.png (value range: {vmin:.2f}–{vmax:.2f})")
    except Exception as e:
        print(f"Error reading raster: {e}")
        with open("/workspace/output/error.txt", "w") as f:
            f.write(f"Failed to render spatial map: {e}")
