import { useState } from "react";
import { useExplorer } from "../../hooks/useExplorer";
import { SearchForm } from "./SearchForm";
import { ItemList } from "./ItemList";
import { ItemDetail } from "./ItemDetail";
import { CodeSnippet } from "./CodeSnippet";

type Tab = "search" | "results";

export function ExplorerPanel() {
  const { explorerResults, selectedItem, explorerLoading, selectItem, showOnMap, drawnBbox } = useExplorer();
  const [tab, setTab] = useState<Tab>("search");

  // Auto-switch to results tab when search completes
  const hasResults = explorerResults && explorerResults.features.length > 0;

  return (
    <div className="flex flex-col h-full">
      {/* Tabs */}
      <div className="flex border-b border-slate-200 shrink-0">
        <button
          onClick={() => setTab("search")}
          className={`flex-1 py-2 text-xs font-medium transition-colors ${
            tab === "search"
              ? "text-purple-700 border-b-2 border-purple-600"
              : "text-slate-500 hover:text-slate-700"
          }`}
        >
          Search
        </button>
        <button
          onClick={() => setTab("results")}
          className={`flex-1 py-2 text-xs font-medium transition-colors ${
            tab === "results"
              ? "text-purple-700 border-b-2 border-purple-600"
              : "text-slate-500 hover:text-slate-700"
          }`}
        >
          Results
          {explorerResults && (
            <span className="ml-1 text-[10px] text-slate-400">
              ({explorerResults.features.length})
            </span>
          )}
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-3">
        {tab === "search" && <SearchForm />}

        {tab === "results" && (
          <div className="space-y-4">
            {explorerLoading && (
              <p className="text-xs text-slate-500 animate-pulse">Searching...</p>
            )}

            {!explorerLoading && !hasResults && (
              <p className="text-xs text-slate-400 italic">
                No results yet. Use the Search tab to find items.
              </p>
            )}

            {hasResults && (
              <>
                <div>
                  <h3 className="text-xs font-medium text-slate-600 mb-1">
                    {explorerResults.features.length} of{" "}
                    {explorerResults.numberMatched ?? "?"} items
                  </h3>
                  <ItemList
                    features={explorerResults.features}
                    selectedId={selectedItem?.id ?? null}
                    onSelect={selectItem}
                  />
                </div>

                {selectedItem && (
                  <ItemDetail item={selectedItem} onShowOnMap={showOnMap} />
                )}

                <CodeSnippet
                  bbox={drawnBbox}
                  datetime={null}
                  collections={[
                    ...new Set(
                      explorerResults.features
                        .map((f) => f.collection)
                        .filter((c): c is string => !!c),
                    ),
                  ]}
                />
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
