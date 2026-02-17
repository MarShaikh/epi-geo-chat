import { TileLayer } from "react-leaflet";
import { buildTileUrl } from "../../api/stac";
import type { TileLayerConfig } from "../../types/api";

interface Props {
  config: TileLayerConfig;
}

export function TileOverlay({ config }: Props) {
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
    />
  );
}
