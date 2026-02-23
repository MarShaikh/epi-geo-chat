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
        <h4 className="text-sm text-[#0A0A0A] truncate">{item.id}</h4>
        {dt && <p className="text-[10px] text-[#666666] uppercase tracking-[0.1em]">{new Date(dt).toLocaleString()}</p>}
      </div>

      {/* Assets */}
      <div>
        <label className="text-[10px] uppercase tracking-[0.15em] text-[#666666]">Asset</label>
        <select
          value={selectedAsset}
          onChange={(e) => setSelectedAsset(e.target.value)}
          className="w-full text-xs border border-[#0A0A0A] bg-transparent px-2 py-1 mt-1 focus:outline-none"
          style={{ fontFamily: 'var(--font-mono)', borderWidth: '1px' }}
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
        <label className="text-[10px] uppercase tracking-[0.15em] text-[#666666]">Colormap</label>
        <select
          value={colormap}
          onChange={(e) => setColormap(e.target.value)}
          className="w-full text-xs border border-[#0A0A0A] bg-transparent px-2 py-1 mt-1 focus:outline-none"
          style={{ fontFamily: 'var(--font-mono)', borderWidth: '1px' }}
        >
          {COLORMAP_OPTIONS.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
      </div>

      {/* Rescale */}
      <div>
        <label className="text-[10px] uppercase tracking-[0.15em] text-[#666666]">Rescale (min,max)</label>
        <input
          type="text"
          value={rescale}
          onChange={(e) => setRescale(e.target.value)}
          placeholder="0,50"
          className="w-full text-xs border border-[#0A0A0A] bg-transparent px-2 py-1 mt-1 focus:outline-none"
          style={{ fontFamily: 'var(--font-mono)', borderWidth: '1px' }}
        />
      </div>

      {!selectedIsTileable && (
        <p className="text-xs text-[#D9381E] border border-[#D9381E] p-2" style={{ borderWidth: '1px' }}>
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
        className="w-full py-1.5 text-[10px] uppercase tracking-[0.15em] text-[#F2F2EC] bg-[#0A0A0A] hover:bg-[#D9381E] disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        style={{ fontFamily: 'var(--font-mono)' }}
      >
        VIEW ON MAP
      </button>

      {/* Properties */}
      <details className="text-xs">
        <summary className="cursor-pointer text-[#666666] uppercase tracking-[0.1em] text-[10px]">Properties</summary>
        <div className="mt-1 bg-[#0A0A0A] p-2 max-h-40 overflow-auto">
          <pre className="whitespace-pre-wrap break-all text-[11px] text-[#F2F2EC]" style={{ fontFamily: 'var(--font-mono)' }}>
            {JSON.stringify(item.properties, null, 2)}
          </pre>
        </div>
      </details>
    </div>
  );
}
