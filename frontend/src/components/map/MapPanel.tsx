import { useState } from "react";
import { MapContainer, TileLayer } from "react-leaflet";
import { useMap } from "../../hooks/useMap";
import { useAppState } from "../../context/AppContext";
import { useExplorer } from "../../hooks/useExplorer";
import { BBoxLayer } from "./BBoxLayer";
import { MapUpdater } from "./MapControls";
import { DrawControl } from "./DrawControl";
import { TileOverlay } from "./TileOverlay";

// Default center: Nigeria
const DEFAULT_CENTER: [number, number] = [9.0, 8.0];
const DEFAULT_ZOOM = 6;

export function MapPanel() {
  const { mode } = useAppState();
  const { bboxBounds, searchedBounds, latestResponse } = useMap();
  const { drawnBbox, setDrawnBbox, activeTileLayer } = useExplorer();
  const [drawing, setDrawing] = useState(false);

  const collectionLabel = latestResponse?.stac_results?.collections?.join(", ") ?? "";
  const countLabel = latestResponse?.stac_results?.count;
  const bboxLabel = countLabel != null
    ? `${collectionLabel} (${countLabel} items)`
    : collectionLabel;

  // Convert drawn bbox to Leaflet bounds for display
  const drawnBounds = drawnBbox
    ? ([[drawnBbox[1], drawnBbox[0]], [drawnBbox[3], drawnBbox[2]]] as [[number, number], [number, number]])
    : null;

  return (
    <div className="relative h-full w-full">
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

        {/* Chat mode layers */}
        {bboxBounds && <BBoxLayer bounds={bboxBounds} color="#3b82f6" label={bboxLabel} />}
        {searchedBounds && searchedBounds !== bboxBounds && (
          <BBoxLayer bounds={searchedBounds} color="#ef4444" label="Search area" />
        )}

        {/* Explorer mode layers */}
        {drawnBounds && <BBoxLayer bounds={drawnBounds} color="#8b5cf6" label="Drawn area" />}
        {activeTileLayer && <TileOverlay config={activeTileLayer} />}

        <DrawControl
          active={drawing}
          onDrawn={(bbox) => {
            setDrawnBbox(bbox);
            setDrawing(false);
          }}
        />
        <MapUpdater bounds={mode === "explorer" ? drawnBounds : (bboxBounds ?? searchedBounds)} />
      </MapContainer>

      {/* Draw button overlay (explorer mode only) */}
      {mode === "explorer" && (
        <div className="absolute top-3 right-3 z-[1000]">
          <button
            onClick={() => {
              if (drawing) {
                setDrawing(false);
              } else {
                setDrawnBbox(null);
                setDrawing(true);
              }
            }}
            className={`px-3 py-1.5 text-sm rounded shadow-md transition-colors ${
              drawing
                ? "bg-purple-600 text-white"
                : "bg-white text-slate-700 hover:bg-slate-50 border border-slate-300"
            }`}
          >
            {drawing ? "Cancel" : "Draw Area"}
          </button>
        </div>
      )}
    </div>
  );
}
