"""
Task type: spatial_map
Description: Render a raster as a semi-transparent image overlay on an interactive Folium map.
Use case: Exploring spatial data interactively — pan, zoom, and inspect values on a web map.
Input: /workspace/input/data.json with at least one raster item and a bbox field.
Output: /workspace/output/map.html — interactive Leaflet/Folium map with the raster overlaid.
"""

import base64
import io
import json

import folium
import matplotlib
import matplotlib.colors as mcolors
import numpy as np
import rasterio
from rasterio.windows import from_bounds
from PIL import Image

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


def arr_to_png_bytes(arr: np.ndarray, colormap: str = "viridis") -> bytes:
    """Convert a 2D float array to a colorised RGBA PNG in memory."""
    valid = arr[~np.isnan(arr)]
    vmin = float(np.percentile(valid, 2)) if len(valid) > 0 else 0.0
    vmax = float(np.percentile(valid, 98)) if len(valid) > 0 else 1.0
    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
    cmap = matplotlib.colormaps[colormap]
    rgba = cmap(norm(arr), bytes=True)  # H x W x 4 uint8
    # Make NaN pixels transparent
    mask = np.isnan(arr)
    rgba[mask, 3] = 0
    img = Image.fromarray(rgba, mode="RGBA")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


# --- Main ---------------------------------------------------------------------

with open("/workspace/input/data.json") as f:
    data = json.load(f)

items = data.get("items", [])
bbox = data.get("bbox")  # [min_lon, min_lat, max_lon, max_lat]
user_query = data.get("user_query", "Map")

# Use the most recent item with a raster asset
item = None
for candidate in reversed(items):
    if get_raster_asset(candidate["assets"]):
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
                img_bounds = [[bbox[1], bbox[0]], [bbox[3], bbox[2]]]  # [[S,W],[N,E]]
            else:
                arr = src.read(1).astype(float)
                b = src.bounds
                img_bounds = [[b.bottom, b.left], [b.top, b.right]]

            nodata = src.nodata
            if nodata is not None:
                arr = np.where(arr == nodata, np.nan, arr)

        # Build Folium map centred on the bbox
        if bbox:
            center = [(bbox[1] + bbox[3]) / 2, (bbox[0] + bbox[2]) / 2]
        else:
            center = [(img_bounds[0][0] + img_bounds[1][0]) / 2,
                      (img_bounds[0][1] + img_bounds[1][1]) / 2]

        m = folium.Map(location=center, zoom_start=8, tiles="CartoDB positron")

        # Convert array to PNG and embed as ImageOverlay
        png_bytes = arr_to_png_bytes(arr, colormap="viridis")
        encoded = base64.b64encode(png_bytes).decode("utf-8")
        img_url = f"data:image/png;base64,{encoded}"

        folium.raster_layers.ImageOverlay(
            image=img_url,
            bounds=img_bounds,
            opacity=0.7,
            name=item.get("id", "Raster"),
        ).add_to(m)

        folium.LayerControl().add_to(m)
        m.get_root().html.add_child(
            folium.Element(f"<h4 style='text-align:center'>{user_query}</h4>")
        )

        m.save("/workspace/output/map.html")
        print("Saved map.html")
    except Exception as e:
        print(f"Error rendering map: {e}")
        with open("/workspace/output/error.txt", "w") as f:
            f.write(f"Failed to render folium map: {e}")
