import type { STACFeature } from "../../types/api";

interface Props {
  features: STACFeature[];
  selectedId: string | null;
  onSelect: (item: STACFeature) => void;
}

export function ItemList({ features, selectedId, onSelect }: Props) {
  if (features.length === 0) {
    return <p className="text-xs text-[#666666] italic py-2">No items found.</p>;
  }

  return (
    <div className="space-y-1">
      {features.map((f) => {
        const dt = f.properties.datetime as string | null;
        const collection = f.collection ?? "unknown";
        const isSelected = f.id === selectedId;

        return (
          <button
            key={f.id}
            onClick={() => onSelect(f)}
            className={`w-full text-left px-2 py-1.5 text-xs transition-colors border ${
              isSelected
                ? "border-[#0A0A0A] bg-[#0A0A0A]/5"
                : "border-transparent hover:bg-[#0A0A0A]/5"
            }`}
            style={{ borderWidth: '1px' }}
          >
            <p className="text-[#0A0A0A] truncate">{f.id}</p>
            <div className="flex gap-2 text-[#666666] mt-0.5">
              <span className="px-1.5 py-0.5 border border-[#D9381E] text-[#D9381E] text-[10px]" style={{ borderWidth: '1px' }}>
                {collection}
              </span>
              {dt && <span>{new Date(dt).toLocaleDateString()}</span>}
            </div>
          </button>
        );
      })}
    </div>
  );
}
