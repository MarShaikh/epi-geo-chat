import { useEffect } from "react";
import { useMap as useLeafletMap } from "react-leaflet";
import type { LatLngBoundsExpression } from "leaflet";

interface Props {
  bounds: LatLngBoundsExpression | null;
}

/** Flies the map to the given bounds when they change. */
export function MapUpdater({ bounds }: Props) {
  const map = useLeafletMap();

  useEffect(() => {
    if (bounds) {
      map.flyToBounds(bounds, { padding: [40, 40], maxZoom: 10 });
    }
  }, [bounds, map]);

  return null;
}
