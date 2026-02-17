import { useCallback, useEffect } from "react";
import { useAppDispatch, useAppState } from "../context/AppContext";
import { fetchCollections, searchItems } from "../api/stac";
import type { STACFeature, STACSearchRequest, TileLayerConfig } from "../types/api";

export function useExplorer() {
  const dispatch = useAppDispatch();
  const { collections, drawnBbox, explorerResults, selectedItem, activeTileLayer, explorerLoading, explorerError } = useAppState();

  // Load collections on first render
  useEffect(() => {
    if (collections.length > 0) return;
    fetchCollections()
      .then((cols) => dispatch({ type: "SET_COLLECTIONS", collections: cols }))
      .catch((e) => {
        console.error("Failed to load collections:", e);
        dispatch({ type: "SET_EXPLORER_ERROR", error: `Failed to load collections: ${e.message}` });
      });
  }, [collections.length, dispatch]);

  const setDrawnBbox = useCallback(
    (bbox: number[] | null) => dispatch({ type: "SET_DRAWN_BBOX", bbox }),
    [dispatch],
  );

  const search = useCallback(
    async (params: STACSearchRequest) => {
      dispatch({ type: "SET_EXPLORER_LOADING", loading: true });
      dispatch({ type: "SET_EXPLORER_ERROR", error: null });
      dispatch({ type: "SET_SELECTED_ITEM", item: null });
      dispatch({ type: "SET_ACTIVE_TILE_LAYER", config: null });
      try {
        const results = await searchItems(params);
        dispatch({ type: "SET_EXPLORER_RESULTS", results });
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        console.error("Search failed:", e);
        dispatch({ type: "SET_EXPLORER_ERROR", error: msg });
        dispatch({ type: "SET_EXPLORER_RESULTS", results: null });
      } finally {
        dispatch({ type: "SET_EXPLORER_LOADING", loading: false });
      }
    },
    [dispatch],
  );

  const selectItem = useCallback(
    (item: STACFeature | null) => dispatch({ type: "SET_SELECTED_ITEM", item }),
    [dispatch],
  );

  const showOnMap = useCallback(
    (config: TileLayerConfig | null) => dispatch({ type: "SET_ACTIVE_TILE_LAYER", config }),
    [dispatch],
  );

  const clearAll = useCallback(() => {
    dispatch({ type: "SET_EXPLORER_RESULTS", results: null });
    dispatch({ type: "SET_SELECTED_ITEM", item: null });
    dispatch({ type: "SET_ACTIVE_TILE_LAYER", config: null });
    dispatch({ type: "SET_DRAWN_BBOX", bbox: null });
    dispatch({ type: "SET_EXPLORER_ERROR", error: null });
  }, [dispatch]);

  return {
    collections,
    drawnBbox,
    setDrawnBbox,
    explorerResults,
    selectedItem,
    activeTileLayer,
    explorerLoading,
    explorerError,
    search,
    selectItem,
    showOnMap,
    clearAll,
  };
}
