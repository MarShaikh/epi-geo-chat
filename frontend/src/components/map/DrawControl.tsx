import { useEffect, useRef, useState } from "react";
import { useMapEvents, Rectangle } from "react-leaflet";
import L from "leaflet";

interface Props {
  active: boolean;
  onDrawn: (bbox: number[]) => void;
}

/**
 * Custom rectangle drawing control using Leaflet mouse events.
 * When `active` is true, click-and-drag draws a rectangle.
 */
export function DrawControl({ active, onDrawn }: Props) {
  const [start, setStart] = useState<L.LatLng | null>(null);
  const [current, setCurrent] = useState<L.LatLng | null>(null);
  const activeRef = useRef(active);
  activeRef.current = active;

  const map = useMapEvents({
    mousedown(e) {
      if (!activeRef.current) return;
      map.dragging.disable();
      setStart(e.latlng);
      setCurrent(e.latlng);
    },
    mousemove(e) {
      if (!activeRef.current || !start) return;
      setCurrent(e.latlng);
    },
    mouseup(e) {
      if (!activeRef.current || !start) return;
      map.dragging.enable();
      const end = e.latlng;
      // bbox: [min_lon, min_lat, max_lon, max_lat]
      const bbox = [
        Math.min(start.lng, end.lng),
        Math.min(start.lat, end.lat),
        Math.max(start.lng, end.lng),
        Math.max(start.lat, end.lat),
      ];
      setStart(null);
      setCurrent(null);
      onDrawn(bbox);
    },
  });

  // Change cursor when drawing mode is active
  useEffect(() => {
    const container = map.getContainer();
    if (active) {
      container.style.cursor = "crosshair";
    } else {
      container.style.cursor = "";
      setStart(null);
      setCurrent(null);
    }
    return () => {
      container.style.cursor = "";
    };
  }, [active, map]);

  if (!start || !current) return null;

  const bounds: L.LatLngBoundsExpression = [
    [Math.min(start.lat, current.lat), Math.min(start.lng, current.lng)],
    [Math.max(start.lat, current.lat), Math.max(start.lng, current.lng)],
  ];

  return (
    <Rectangle
      bounds={bounds}
      pathOptions={{ color: "#8b5cf6", weight: 2, fillOpacity: 0.15, dashArray: "6 4" }}
    />
  );
}
