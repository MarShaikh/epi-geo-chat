import { TileLayer } from "react-leaflet";
import { buildTileUrl } from "../../api/stac";
import type { TileLayerConfig } from "../../types/api";
import type { LatLngBoundsExpression } from "leaflet";

interface Props {
  config: TileLayerConfig;
  bounds?: LatLngBoundsExpression | null;
}

export function TileOverlay({ config, bounds }: Props) {
  const url = buildTileUrl(config.collectionId, config.itemId, config.assets, {
    colormap: config.colormap,
    rescale: config.rescale,
    assetBidx: config.assetBidx,
  });

  return (
    <TileLayer
      key={`${config.collectionId}-${config.itemId}-${config.assets}-${config.colormap}`}
      url={url}
      opacity={0.7}
      maxZoom={18}
      bounds={bounds ?? undefined}
    />
  );
}
