import { useMemo, useState } from "react";
import type { STACFeature, TileLayerConfig } from "../../types/api";

interface Props {
  item: STACFeature;
  onShowOnMap: (config: TileLayerConfig) => void;
}

const COLORMAP_OPTIONS = ["viridis", "Blues", "Reds", "Greens", "terrain", "coolwarm", "magma", "plasma"];

/** Non-renderable asset types that the Tiler can't handle. */
const NON_TILEABLE = ["application/x-hdf", "application/x-hdf5", "text/xml", "application/xml"];

function isTileable(asset: { type?: string }): boolean {
  if (!asset.type) return true; // no type info — assume it works
  const t = asset.type.toLowerCase();
  return !NON_TILEABLE.some((nt) => t.includes(nt));
}

export function ItemDetail({ item, onShowOnMap }: Props) {
  const allAssetKeys = Object.keys(item.assets);

  // Separate tileable (COG) assets from non-tileable (HDF, XML)
  const tileableKeys = useMemo(
    () => allAssetKeys.filter((k) => isTileable(item.assets[k])),
    [allAssetKeys, item.assets],
  );

  // Default to first tileable asset, not the first overall
  const defaultAsset = tileableKeys[0] ?? allAssetKeys[0] ?? "data";

  const [selectedAsset, setSelectedAsset] = useState(defaultAsset);
  const [colormap, setColormap] = useState("viridis");
  const [rescale, setRescale] = useState("0,50");
  const collection = item.collection ?? "";

  const dt = item.properties.datetime as string | null;
  const selectedIsTileable = isTileable(item.assets[selectedAsset] ?? {});

  return (
    <div className="space-y-3">
      <div>
        <h4 className="text-sm font-semibold text-slate-700 truncate">{item.id}</h4>
        {dt && <p className="text-xs text-slate-500">{new Date(dt).toLocaleString()}</p>}
      </div>

      {/* Assets */}
      <div>
        <label className="text-xs font-medium text-slate-600">Asset</label>
        <select
          value={selectedAsset}
          onChange={(e) => setSelectedAsset(e.target.value)}
          className="w-full text-xs border border-slate-300 rounded px-2 py-1"
        >
          {allAssetKeys.map((k) => {
            const tileable = isTileable(item.assets[k]);
            return (
              <option key={k} value={k}>
                {item.assets[k].title ?? k}{!tileable ? " (not renderable)" : ""}
              </option>
            );
          })}
        </select>
      </div>

      {/* Colormap */}
      <div>
        <label className="text-xs font-medium text-slate-600">Colormap</label>
        <select
          value={colormap}
          onChange={(e) => setColormap(e.target.value)}
          className="w-full text-xs border border-slate-300 rounded px-2 py-1"
        >
          {COLORMAP_OPTIONS.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
      </div>

      {/* Rescale */}
      <div>
        <label className="text-xs font-medium text-slate-600">Rescale (min,max)</label>
        <input
          type="text"
          value={rescale}
          onChange={(e) => setRescale(e.target.value)}
          placeholder="0,50"
          className="w-full text-xs border border-slate-300 rounded px-2 py-1"
        />
      </div>

      {!selectedIsTileable && (
        <p className="text-xs text-amber-600 bg-amber-50 rounded p-2">
          This asset format (e.g. HDF) can't be rendered on the map. Select a GeoTIFF (COG) asset instead, or use the download code snippet.
        </p>
      )}

      <button
        onClick={() =>
          onShowOnMap({
            collectionId: collection,
            itemId: item.id,
            assets: selectedAsset,
            colormap,
            rescale,
          })
        }
        disabled={!selectedIsTileable}
        className="w-full py-1.5 text-sm font-medium text-white bg-blue-600 rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        View on Map
      </button>

      {/* Properties */}
      <details className="text-xs">
        <summary className="cursor-pointer text-slate-600 font-medium">Properties</summary>
        <div className="mt-1 bg-slate-50 rounded p-2 max-h-40 overflow-auto">
          <pre className="whitespace-pre-wrap break-all text-[11px] text-slate-600">
            {JSON.stringify(item.properties, null, 2)}
          </pre>
        </div>
      </details>
    </div>
  );
}
