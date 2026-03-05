"""
Task type: statistics
Description: Compute per-item summary statistics (min, max, mean, std, median) across all raster items.
Use case: Generating a summary table of any gridded variable across time or space.
Input: /workspace/input/data.json with one or more raster items.
Output: /workspace/output/summary_stats.csv — table with one row per item.
         /workspace/output/summary_stats.png — bar chart of mean values with error bars (std).
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


# --- Main ---------------------------------------------------------------------

with open("/workspace/input/data.json") as f:
    data = json.load(f)

items = data.get("items", [])
user_query = data.get("user_query", "Summary Statistics")
print(f"Computing statistics for {len(items)} items...")

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

        records.append({
            "item_id": item["id"],
            "datetime": item.get("datetime", ""),
            "min": float(np.nanmin(arr)),
            "max": float(np.nanmax(arr)),
            "mean": float(np.nanmean(arr)),
            "std": float(np.nanstd(arr)),
            "median": float(np.nanmedian(arr)),
            "valid_pixels": int(np.sum(~np.isnan(arr))),
        })
        print(f"  {item['id']}: mean={records[-1]['mean']:.4f}, std={records[-1]['std']:.4f}")
    except Exception as e:
        print(f"  Skipping {item['id']} — error: {e}")

if not records:
    with open("/workspace/output/no_data.txt", "w") as f:
        f.write("No renderable raster assets were found in the provided items.")
    print("No data to summarise.")
else:
    df = pd.DataFrame(records)
    if "datetime" in df.columns and df["datetime"].any():
        df["datetime"] = pd.to_datetime(df["datetime"])
        df = df.sort_values("datetime")

    df.to_csv("/workspace/output/summary_stats.csv", index=False)
    print(f"Saved summary_stats.csv ({len(df)} rows)")

    # Bar chart of mean values with std error bars
    labels = df["datetime"].dt.strftime("%Y-%m-%d") if pd.api.types.is_datetime64_any_dtype(df["datetime"]) else df["item_id"]
    fig, ax = plt.subplots(figsize=(max(8, len(df) * 0.8), 5))
    ax.bar(range(len(df)), df["mean"], yerr=df["std"], capsize=4, color="steelblue", alpha=0.8)
    ax.set_xticks(range(len(df)))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8)
    ax.set_title(f"Summary Statistics — {user_query}")
    ax.set_ylabel("Mean Value (± Std Dev)")
    ax.grid(True, axis="y", alpha=0.3)
    plt.tight_layout()
    plt.savefig("/workspace/output/summary_stats.png", dpi=150, bbox_inches="tight")
    plt.close()
    print("Saved summary_stats.png")
