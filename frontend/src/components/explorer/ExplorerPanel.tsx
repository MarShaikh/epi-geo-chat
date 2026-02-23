import { useExplorer } from "../../hooks/useExplorer";
import { SearchForm } from "./SearchForm";
import { ItemList } from "./ItemList";
import { ItemDetail } from "./ItemDetail";
import { CodeSnippet } from "./CodeSnippet";

export function ExplorerPanel() {
  const { explorerResults, selectedItem, explorerLoading, explorerError, selectItem, showOnMap, drawnBbox } = useExplorer();

  const hasResults = explorerResults && explorerResults.features.length > 0;

  return (
    <div className="flex flex-col h-full overflow-y-auto">
      {/* Search form — always visible */}
      <div className="p-3 border-b border-[#0A0A0A]" style={{ borderWidth: '1.5px' }}>
        <SearchForm />
      </div>

      {/* Results — shown inline below */}
      <div className="flex-1 p-3 space-y-4">
        {explorerLoading && (
          <p className="text-[10px] uppercase tracking-[0.1em] text-[#666666]" style={{ animation: 'pulse 2s ease-in-out infinite' }}>Searching...</p>
        )}

        {explorerError && (
          <div className="text-xs text-[#D9381E] border border-[#D9381E] p-2" style={{ borderWidth: '1.5px' }}>
            {explorerError}
          </div>
        )}

        {!explorerLoading && !hasResults && !explorerError && explorerResults !== null && (
          <p className="text-xs text-[#666666] italic">No items found for this search.</p>
        )}

        {hasResults && (
          <>
            <div>
              <h3 className="text-[10px] uppercase tracking-[0.1em] text-[#666666] mb-1" style={{ fontFamily: 'var(--font-mono)' }}>
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
    </div>
  );
}
