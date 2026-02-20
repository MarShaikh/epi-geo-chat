import { ImageOverlay } from "react-leaflet";
import { buildBboxImageUrl } from "../../api/stac";
import type { TileLayerConfig } from "../../types/api";
import type { LatLngBoundsExpression } from "leaflet";

interface Props {
  config: TileLayerConfig;
  bounds: LatLngBoundsExpression;
  bbox: number[];
}

export function TileOverlay({ config, bounds, bbox }: Props) {
  const url = buildBboxImageUrl(config.collectionId, config.itemId, bbox, config.assets, {
    colormap: config.colormap,
    rescale: config.rescale,
    assetBidx: config.assetBidx,
  });

  return (
    <ImageOverlay
      key={`${config.collectionId}-${config.itemId}-${config.assets}-${config.colormap}-${bbox.join(",")}`}
      url={url}
      bounds={bounds}
      opacity={0.7}
    />
  );
}
