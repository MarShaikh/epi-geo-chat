import { useState, useCallback } from "react";
import { MapContainer, TileLayer, useMapEvents } from "react-leaflet";
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

function CoordinateTracker({ onMove }: { onMove: (lat: number, lng: number) => void }) {
  useMapEvents({
    mousemove(e) {
      onMove(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
}

export function MapPanel() {
  const { mode } = useAppState();
  const { bboxBounds, searchedBounds, latestResponse } = useMap();
  const { drawnBbox, setDrawnBbox, activeTileLayer, clearAll } = useExplorer();
  const [drawing, setDrawing] = useState(false);
  const [coords, setCoords] = useState<{ lat: number; lng: number } | null>(null);

  const handleMouseMove = useCallback((lat: number, lng: number) => {
    setCoords({ lat, lng });
  }, []);

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
        zoomControl={false}
      >
        <TileLayer
          attribution='&copy; <a href="https://carto.com/">CARTO</a>'
          url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
        />

        {/* Chat mode layers */}
        {bboxBounds && <BBoxLayer bounds={bboxBounds} color="#D9381E" label={bboxLabel} />}
        {searchedBounds && searchedBounds !== bboxBounds && (
          <BBoxLayer bounds={searchedBounds} color="#0A0A0A" label="Search area" />
        )}

        {/* Explorer mode layers */}
        {drawnBounds && <BBoxLayer bounds={drawnBounds} color="#D9381E" label="Drawn area" />}
        {activeTileLayer && drawnBounds && drawnBbox && (
          <TileOverlay config={activeTileLayer} bounds={drawnBounds} bbox={drawnBbox} />
        )}

        <DrawControl
          active={drawing}
          onDrawn={(bbox) => {
            setDrawnBbox(bbox);
            setDrawing(false);
          }}
        />
        <MapUpdater bounds={mode === "explorer" ? drawnBounds : (bboxBounds ?? searchedBounds)} />
        <CoordinateTracker onMove={handleMouseMove} />
      </MapContainer>

      {/* Crosshair overlay */}
      <div className="absolute inset-0 pointer-events-none z-[999] flex items-center justify-center">
        <div className="w-px h-5 bg-[#D9381E] opacity-60" />
      </div>
      <div className="absolute inset-0 pointer-events-none z-[999] flex items-center justify-center">
        <div className="h-px w-5 bg-[#D9381E] opacity-60" />
      </div>

      {/* Coordinate display */}
      {coords && (
        <div
          className="absolute bottom-3 left-3 z-[1000] border border-[#0A0A0A] bg-[#F2F2EC] px-2 py-1 text-[10px] uppercase tracking-[0.1em]"
          style={{ fontFamily: 'var(--font-mono)', borderWidth: '1.5px' }}
        >
          {coords.lat.toFixed(4)}, {coords.lng.toFixed(4)}
        </div>
      )}

      {/* Map overlay buttons (explorer mode only) */}
      {mode === "explorer" && (
        <div className="absolute top-3 right-3 z-[1000] pointer-events-none flex gap-2">
          <button
            onClick={() => {
              if (drawing) {
                setDrawing(false);
              } else {
                setDrawnBbox(null);
                setDrawing(true);
              }
            }}
            className={`pointer-events-auto px-3 py-1.5 text-[10px] uppercase tracking-[0.1em] transition-colors border border-[#0A0A0A] ${
              drawing
                ? "bg-[#D9381E] text-[#F2F2EC] border-[#D9381E]"
                : "bg-[#F2F2EC] text-[#0A0A0A] hover:bg-[#0A0A0A] hover:text-[#F2F2EC]"
            }`}
            style={{ fontFamily: 'var(--font-mono)', borderWidth: '1.5px' }}
          >
            {drawing ? "CANCEL" : "DRAW AREA"}
          </button>
          {(drawnBbox || activeTileLayer) && (
            <button
              onClick={clearAll}
              className="pointer-events-auto px-3 py-1.5 text-[10px] uppercase tracking-[0.1em] border border-[#0A0A0A] bg-[#F2F2EC] text-[#D9381E] hover:bg-[#D9381E] hover:text-[#F2F2EC] hover:border-[#D9381E] transition-colors"
              style={{ fontFamily: 'var(--font-mono)', borderWidth: '1.5px' }}
            >
              CLEAR
            </button>
          )}
        </div>
      )}
    </div>
  );
}
