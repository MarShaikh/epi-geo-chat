import { useState } from "react";
import type { STACFeature, TileLayerConfig } from "../../types/api";

interface Props {
  item: STACFeature;
  onShowOnMap: (config: TileLayerConfig) => void;
}

const COLORMAP_OPTIONS = ["viridis", "Blues", "Reds", "Greens", "terrain", "coolwarm", "magma", "plasma"];

export function ItemDetail({ item, onShowOnMap }: Props) {
  const assetKeys = Object.keys(item.assets);
  const [selectedAsset, setSelectedAsset] = useState(assetKeys[0] ?? "data");
  const [colormap, setColormap] = useState("viridis");
  const [rescale, setRescale] = useState("0,50");
  const collection = item.collection ?? "";

  const dt = item.properties.datetime as string | null;

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
          {assetKeys.map((k) => (
            <option key={k} value={k}>
              {item.assets[k].title ?? k}
            </option>
          ))}
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
        className="w-full py-1.5 text-sm font-medium text-white bg-blue-600 rounded hover:bg-blue-700 transition-colors"
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
