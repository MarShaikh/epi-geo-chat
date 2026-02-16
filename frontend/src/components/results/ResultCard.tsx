import type { STACItem } from "../../types/api";

interface Props {
  item: STACItem;
}

export function ResultCard({ item }: Props) {
  return (
    <div className="border border-slate-200 rounded-md p-2 text-xs">
      <p className="font-medium text-slate-800 truncate" title={item.id}>
        {item.id}
      </p>
      {item.datetime && item.datetime !== "Unspecified" && (
        <p className="text-slate-500 mt-0.5">{item.datetime}</p>
      )}
      {item.assets.length > 0 && (
        <div className="flex gap-1 mt-1 flex-wrap">
          {item.assets.map((asset) => (
            <span key={asset} className="px-1.5 py-0.5 bg-slate-100 rounded text-slate-600">
              {asset}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
