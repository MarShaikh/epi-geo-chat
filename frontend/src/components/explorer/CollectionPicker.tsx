import type { STACCollection } from "../../types/api";

interface Props {
  collections: STACCollection[];
  selected: string[];
  onChange: (ids: string[]) => void;
}

export function CollectionPicker({ collections, selected, onChange }: Props) {
  return (
    <div className="space-y-1">
      <label className="text-xs font-medium text-slate-600">Collections</label>
      <div className="space-y-1">
        {collections.map((c) => (
          <label
            key={c.id}
            className="flex items-start gap-2 p-1.5 rounded hover:bg-slate-50 cursor-pointer"
          >
            <input
              type="checkbox"
              checked={selected.includes(c.id)}
              onChange={(e) => {
                if (e.target.checked) {
                  onChange([...selected, c.id]);
                } else {
                  onChange(selected.filter((id) => id !== c.id));
                }
              }}
              className="mt-0.5"
            />
            <div className="min-w-0">
              <p className="text-sm font-medium text-slate-700 truncate">{c.title ?? c.id}</p>
              {c.description && (
                <p className="text-xs text-slate-500 line-clamp-2">{c.description}</p>
              )}
            </div>
          </label>
        ))}
      </div>
    </div>
  );
}
