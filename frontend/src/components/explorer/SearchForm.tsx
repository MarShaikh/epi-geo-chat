import { useState } from "react";
import { useExplorer } from "../../hooks/useExplorer";
import { CollectionPicker } from "./CollectionPicker";
import type { STACSearchRequest } from "../../types/api";

export function SearchForm() {
  const { collections, drawnBbox, search, explorerLoading } = useExplorer();
  const [selectedCollections, setSelectedCollections] = useState<string[]>([]);
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [limit, setLimit] = useState(20);

  const handleSearch = () => {
    const params: STACSearchRequest = { limit };
    if (drawnBbox) params.bbox = drawnBbox;
    if (selectedCollections.length > 0) params.collections = selectedCollections;
    if (startDate && endDate) {
      params.datetime = `${startDate}T00:00:00Z/${endDate}T23:59:59Z`;
    } else if (startDate) {
      params.datetime = `${startDate}T00:00:00Z/..`;
    } else if (endDate) {
      params.datetime = `../${endDate}T23:59:59Z`;
    }
    search(params);
  };

  return (
    <div className="space-y-3">
      <CollectionPicker
        collections={collections}
        selected={selectedCollections}
        onChange={setSelectedCollections}
      />

      {/* Bounding box display */}
      <div>
        <label className="text-xs font-medium text-slate-600">Bounding Box</label>
        {drawnBbox ? (
          <p className="text-xs text-slate-700 bg-slate-50 rounded px-2 py-1 font-mono">
            {drawnBbox.map((n) => n.toFixed(4)).join(", ")}
          </p>
        ) : (
          <p className="text-xs text-slate-400 italic">Draw an area on the map</p>
        )}
      </div>

      {/* Date range */}
      <div className="grid grid-cols-2 gap-2">
        <div>
          <label className="text-xs font-medium text-slate-600">Start Date</label>
          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className="w-full text-xs border border-slate-300 rounded px-2 py-1"
          />
        </div>
        <div>
          <label className="text-xs font-medium text-slate-600">End Date</label>
          <input
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            className="w-full text-xs border border-slate-300 rounded px-2 py-1"
          />
        </div>
      </div>

      {/* Limit */}
      <div>
        <label className="text-xs font-medium text-slate-600">Max Results</label>
        <input
          type="number"
          value={limit}
          min={1}
          max={100}
          onChange={(e) => setLimit(Number(e.target.value))}
          className="w-full text-xs border border-slate-300 rounded px-2 py-1"
        />
      </div>

      <button
        onClick={handleSearch}
        disabled={explorerLoading}
        className="w-full py-1.5 text-sm font-medium text-white bg-purple-600 rounded hover:bg-purple-700 disabled:opacity-50 transition-colors"
      >
        {explorerLoading ? "Searching..." : "Search"}
      </button>
    </div>
  );
}
