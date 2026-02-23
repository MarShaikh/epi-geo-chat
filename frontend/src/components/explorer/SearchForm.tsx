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
        <label className="text-[10px] uppercase tracking-[0.15em] text-[#666666]">Bounding Box</label>
        {drawnBbox ? (
          <p className="text-xs text-[#0A0A0A] mt-1" style={{ fontFamily: 'var(--font-mono)' }}>
            {drawnBbox.map((n) => n.toFixed(4)).join(", ")}
          </p>
        ) : (
          <p className="text-xs text-[#666666] italic mt-1">Draw an area on the map</p>
        )}
      </div>

      {/* Date range */}
      <div className="grid grid-cols-2 gap-2">
        <div>
          <label className="text-[10px] uppercase tracking-[0.15em] text-[#666666]">Start Date</label>
          <input
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            className="w-full text-xs border border-[#0A0A0A] bg-transparent px-2 py-1 mt-1 focus:outline-none"
            style={{ fontFamily: 'var(--font-mono)', borderWidth: '1px' }}
          />
        </div>
        <div>
          <label className="text-[10px] uppercase tracking-[0.15em] text-[#666666]">End Date</label>
          <input
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            className="w-full text-xs border border-[#0A0A0A] bg-transparent px-2 py-1 mt-1 focus:outline-none"
            style={{ fontFamily: 'var(--font-mono)', borderWidth: '1px' }}
          />
        </div>
      </div>

      {/* Limit */}
      <div>
        <label className="text-[10px] uppercase tracking-[0.15em] text-[#666666]">Max Results</label>
        <input
          type="number"
          value={limit}
          min={1}
          max={100}
          onChange={(e) => setLimit(Number(e.target.value))}
          className="w-full text-xs border border-[#0A0A0A] bg-transparent px-2 py-1 mt-1 focus:outline-none"
          style={{ fontFamily: 'var(--font-mono)', borderWidth: '1px' }}
        />
      </div>

      <button
        onClick={handleSearch}
        disabled={explorerLoading}
        className="w-full py-1.5 text-[10px] uppercase tracking-[0.15em] text-[#F2F2EC] bg-[#0A0A0A] hover:bg-[#D9381E] disabled:opacity-50 transition-colors"
        style={{ fontFamily: 'var(--font-mono)' }}
      >
        {explorerLoading ? "SEARCHING..." : "SEARCH"}
      </button>
    </div>
  );
}
