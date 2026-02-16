import { Rectangle, Popup } from "react-leaflet";
import type { LatLngBoundsExpression } from "leaflet";

interface Props {
  bounds: LatLngBoundsExpression;
  color?: string;
  label?: string;
}

export function BBoxLayer({ bounds, color = "#3b82f6", label }: Props) {
  return (
    <Rectangle
      bounds={bounds}
      pathOptions={{ color, weight: 2, fillOpacity: 0.1 }}
    >
      {label && <Popup>{label}</Popup>}
    </Rectangle>
  );
}
