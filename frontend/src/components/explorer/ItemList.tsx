import type { STACFeature } from "../../types/api";

interface Props {
  features: STACFeature[];
  selectedId: string | null;
  onSelect: (item: STACFeature) => void;
}

export function ItemList({ features, selectedId, onSelect }: Props) {
  if (features.length === 0) {
    return <p className="text-xs text-slate-400 italic py-2">No items found.</p>;
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
            className={`w-full text-left px-2 py-1.5 rounded text-xs transition-colors ${
              isSelected
                ? "bg-purple-50 border border-purple-300"
                : "bg-slate-50 hover:bg-slate-100 border border-transparent"
            }`}
          >
            <p className="font-medium text-slate-700 truncate">{f.id}</p>
            <div className="flex gap-2 text-slate-500 mt-0.5">
              <span className="px-1.5 py-0.5 bg-blue-50 text-blue-700 rounded-full text-[10px] font-medium">
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
