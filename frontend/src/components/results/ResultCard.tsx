import type { STACItem } from "../../types/api";

interface Props {
  item: STACItem;
}

export function ResultCard({ item }: Props) {
  return (
    <div className="border border-[#0A0A0A] p-2 text-xs" style={{ borderWidth: '1px' }}>
      <p className="text-[#0A0A0A] truncate" title={item.id}>
        {item.id}
      </p>
      {item.datetime && item.datetime !== "Unspecified" && (
        <p className="text-[#666666] mt-0.5">{item.datetime}</p>
      )}
      {item.assets.length > 0 && (
        <div className="flex gap-1 mt-1 flex-wrap">
          {item.assets.map((asset) => (
            <span key={asset} className="px-1.5 py-0.5 border border-[#0A0A0A] text-[#0A0A0A] text-[10px]" style={{ borderWidth: '1px' }}>
              {asset}
            </span>
          ))}
        </div>
      )}
    </div>
  );
}
