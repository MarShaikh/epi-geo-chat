import { useMemo } from "react";
import { useAppState } from "../context/AppContext";
import type { LatLngBoundsExpression } from "leaflet";

/** Extracts map-relevant data from the latest response. */
export function useMap() {
  const { latestResponse } = useAppState();

  const bboxBounds = useMemo((): LatLngBoundsExpression | null => {
    const bbox = latestResponse?.geocoding?.bbox;
    if (!bbox || bbox.length < 4) return null;
    // bbox is [min_lon, min_lat, max_lon, max_lat]
    return [
      [bbox[1], bbox[0]], // SW corner [lat, lon]
      [bbox[3], bbox[2]], // NE corner [lat, lon]
    ];
  }, [latestResponse]);

  const searchedBounds = useMemo((): LatLngBoundsExpression | null => {
    const bbox = latestResponse?.stac_results?.bbox_searched;
    if (!bbox || bbox.length < 4) return null;
    return [
      [bbox[1], bbox[0]],
      [bbox[3], bbox[2]],
    ];
  }, [latestResponse]);

  return { bboxBounds, searchedBounds, latestResponse };
}
