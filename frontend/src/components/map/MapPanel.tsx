import { MapContainer, TileLayer } from "react-leaflet";
import { useMap } from "../../hooks/useMap";
import { BBoxLayer } from "./BBoxLayer";
import { MapUpdater } from "./MapControls";

// Default center: Nigeria
const DEFAULT_CENTER: [number, number] = [9.0, 8.0];
const DEFAULT_ZOOM = 6;

export function MapPanel() {
  const { bboxBounds, searchedBounds, latestResponse } = useMap();

  const collectionLabel = latestResponse?.stac_results?.collections?.join(", ") ?? "";
  const countLabel = latestResponse?.stac_results?.count;
  const bboxLabel = countLabel != null
    ? `${collectionLabel} (${countLabel} items)`
    : collectionLabel;

  return (
    <MapContainer
      center={DEFAULT_CENTER}
      zoom={DEFAULT_ZOOM}
      className="h-full w-full"
      scrollWheelZoom={true}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {bboxBounds && <BBoxLayer bounds={bboxBounds} color="#3b82f6" label={bboxLabel} />}
      {searchedBounds && searchedBounds !== bboxBounds && (
        <BBoxLayer bounds={searchedBounds} color="#ef4444" label="Search area" />
      )}
      <MapUpdater bounds={bboxBounds ?? searchedBounds} />
    </MapContainer>
  );
}
