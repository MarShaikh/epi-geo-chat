import { useAppState } from "../../context/AppContext";
import { MetadataTable } from "./MetadataTable";
import { ResultCard } from "./ResultCard";

export function ResultsPanel() {
  const { latestResponse } = useAppState();

  if (!latestResponse) {
    return (
      <div className="flex items-center justify-center h-full text-slate-400 text-sm p-4 text-center">
        <p>Search results will appear here after you submit a query.</p>
      </div>
    );
  }

  const { parsed_query, geocoding, stac_results } = latestResponse;

  return (
    <div className="p-3 space-y-4 text-sm">
      {/* Query summary */}
      <section>
        <h3 className="font-semibold text-slate-700 mb-1">Query</h3>
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
          <h3 className="font-semibold text-slate-700 mb-1">Geocoding</h3>
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
        <h3 className="font-semibold text-slate-700 mb-1">
          STAC Results
          {stac_results.count != null && (
            <span className="ml-2 text-xs font-normal text-slate-500">
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
                className="px-2 py-0.5 bg-blue-50 text-blue-700 rounded-full text-xs font-medium"
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
            <p className="text-xs text-slate-500">
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
