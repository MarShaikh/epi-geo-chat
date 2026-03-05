"""
Task type: comparison
Description: Subtract two rasters (earliest vs. latest) to show change over time.
Use case: Before/after comparison, anomaly detection, change analysis for any gridded variable.
Input: /workspace/input/data.json with at least 2 raster items (sorted by datetime).
Output: /workspace/output/temporal_diff.png — side-by-side plot: early | late | difference (diverging colormap).
         /workspace/output/temporal_diff.csv — summary stats of the difference (mean, std, % increased).
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


def read_raster(href: str) -> np.ndarray:
    """Read band 1 of a raster, masking nodata as NaN."""
    with rasterio.open(href) as src:
        arr = src.read(1).astype(float)
        nodata = src.nodata
        if nodata is not None:
            arr = np.where(arr == nodata, np.nan, arr)
        return arr


def match_shapes(arr_a: np.ndarray, arr_b: np.ndarray) -> tuple:
    """Crop both arrays to their overlapping shape if they differ."""
    if arr_a.shape == arr_b.shape:
        return arr_a, arr_b
    h = min(arr_a.shape[0], arr_b.shape[0])
    w = min(arr_a.shape[1], arr_b.shape[1])
    return arr_a[:h, :w], arr_b[:h, :w]


# --- Main ---------------------------------------------------------------------

with open("/workspace/input/data.json") as f:
    data = json.load(f)

items = data.get("items", [])
user_query = data.get("user_query", "Temporal Comparison")

# Sort by datetime and pick first (earliest) and last (latest)
sortable = [(item.get("datetime", ""), item) for item in items if get_raster_asset(item["assets"])]
sortable.sort(key=lambda x: x[0])

if len(sortable) < 2:
    with open("/workspace/output/no_data.txt", "w") as f:
        f.write("Need at least 2 raster items with valid assets to compute a temporal difference.")
    print("Not enough data for comparison.")
else:
    early_dt, early_item = sortable[0]
    late_dt, late_item = sortable[-1]
    print(f"Comparing: {early_item['id']} ({early_dt}) vs {late_item['id']} ({late_dt})")

    try:
        arr_early = read_raster(get_raster_asset(early_item["assets"]))
        arr_late = read_raster(get_raster_asset(late_item["assets"]))
        arr_early, arr_late = match_shapes(arr_early, arr_late)

        diff = arr_late - arr_early

        # Summary stats
        stats = {
            "early_datetime": [early_dt],
            "late_datetime": [late_dt],
            "diff_mean": [float(np.nanmean(diff))],
            "diff_std": [float(np.nanstd(diff))],
            "diff_min": [float(np.nanmin(diff))],
            "diff_max": [float(np.nanmax(diff))],
            "pct_increased": [float(np.nanmean(diff > 0) * 100)],
        }
        pd.DataFrame(stats).to_csv("/workspace/output/temporal_diff.csv", index=False)

        # Plot
        vabs = float(np.nanpercentile(np.abs(diff), 98))
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))

        for ax, arr, title, cmap in [
            (axes[0], arr_early, f"Early\n{early_dt[:10]}", "viridis"),
            (axes[1], arr_late,  f"Late\n{late_dt[:10]}",  "viridis"),
            (axes[2], diff,      "Difference (Late − Early)", "RdBu_r"),
        ]:
            if cmap == "RdBu_r":
                im = ax.imshow(arr, cmap=cmap, vmin=-vabs, vmax=vabs, origin="upper")
            else:
                p1, p99 = np.nanpercentile(arr, [1, 99])
                im = ax.imshow(arr, cmap=cmap, vmin=p1, vmax=p99, origin="upper")
            plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
            ax.set_title(title)
            ax.axis("off")

        fig.suptitle(user_query, fontsize=13)
        plt.tight_layout()
        plt.savefig("/workspace/output/temporal_diff.png", dpi=150, bbox_inches="tight")
        plt.close()
        print(f"Saved temporal_diff.png — mean change: {stats['diff_mean'][0]:.4f}")
    except Exception as e:
        print(f"Error during comparison: {e}")
        with open("/workspace/output/error.txt", "w") as f:
            f.write(f"Failed to compute temporal difference: {e}")
