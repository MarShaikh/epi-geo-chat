import { useAppState } from "../../context/AppContext";
import { MetadataTable } from "./MetadataTable";
import { ResultCard } from "./ResultCard";

export function ResultsPanel() {
  const { latestResponse } = useAppState();

  if (!latestResponse) {
    return (
      <div className="flex items-center justify-center h-full p-6 text-center">
        <div className="border border-dashed border-[#0A0A0A] px-6 py-8" style={{ borderWidth: '1.5px' }}>
          <p className="text-xs uppercase tracking-[0.15em] text-[#666666]">
            Search results will appear here after you submit a query.
          </p>
        </div>
      </div>
    );
  }

  const { parsed_query, geocoding, stac_results } = latestResponse;

  return (
    <div className="p-3 space-y-4 text-sm">
      {/* Query summary */}
      <section>
        <h3 className="text-lg mb-1 border-b border-[#0A0A0A] pb-1" style={{ fontFamily: 'var(--font-serif)', borderWidth: '1px' }}>Query</h3>
        <MetadataTable
          data={{
            intent: parsed_query.intent,
            sub_intent: parsed_query.metadata_sub_intent,
            location: parsed_query.location,
            datetime: parsed_query.datetime,
            keywords: parsed_query.data_type_keywords.join(", ") || null,
          }}
        />
      </section>

      {/* Geocoding */}
      {geocoding.bbox && (
        <section>
          <h3 className="text-lg mb-1 border-b border-[#0A0A0A] pb-1" style={{ fontFamily: 'var(--font-serif)', borderWidth: '1px' }}>Geocoding</h3>
          <MetadataTable
            data={{
              bbox: geocoding.bbox.map((n) => n.toFixed(4)).join(", "),
              datetime: geocoding.datetime,
              source: geocoding.location_source,
            }}
          />
        </section>
      )}

      {/* STAC Results */}
      <section>
        <h3 className="text-lg mb-1 border-b border-[#0A0A0A] pb-1" style={{ fontFamily: 'var(--font-serif)', borderWidth: '1px' }}>
          Analysis Results
          {stac_results.count != null && (
            <span className="ml-2 text-[10px] uppercase tracking-[0.1em] text-[#666666]" style={{ fontFamily: 'var(--font-mono)' }}>
              ({stac_results.count} items)
            </span>
          )}
        </h3>

        {/* Collections */}
        {stac_results.collections.length > 0 && (
          <div className="flex gap-1 flex-wrap mb-2">
            {stac_results.collections.map((c) => (
              <span
                key={c}
                className="px-2 py-0.5 border border-[#D9381E] text-[#D9381E] text-[10px] uppercase tracking-[0.05em]"
                style={{ borderWidth: '1px' }}
              >
                {c}
              </span>
            ))}
          </div>
        )}

        <MetadataTable
          data={{
            date_range: stac_results.date_range,
            description: stac_results.description,
          }}
        />

        {/* Items */}
        {stac_results.items && stac_results.items.length > 0 && (
          <div className="mt-2 space-y-1.5">
            <p className="text-[10px] uppercase tracking-[0.1em] text-[#666666]">
              Showing {stac_results.items.length} of {stac_results.count ?? "?"} items
            </p>
            {stac_results.items.map((item) => (
              <ResultCard key={item.id} item={item} />
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
