import { createContext, useContext, useReducer, type ReactNode, type Dispatch } from "react";
import type { ChatResponse, Message, STACCollection, STACFeatureCollection, STACFeature, TileLayerConfig } from "../types/api";

export type AppMode = "chat" | "explorer";

/** Application state */
export interface AppState {
  mode: AppMode;
  messages: Message[];
  isStreaming: boolean;
  currentStep: number | null;
  currentAgent: string | null;
  latestResponse: ChatResponse | null;
  // Explorer state
  collections: STACCollection[];
  drawnBbox: number[] | null;
  explorerResults: STACFeatureCollection | null;
  selectedItem: STACFeature | null;
  activeTileLayer: TileLayerConfig | null;
  explorerLoading: boolean;
  explorerError: string | null;
}

/** Actions */
type Action =
  | { type: "ADD_MESSAGE"; message: Message }
  | { type: "UPDATE_LAST_ASSISTANT"; content: string; chatResponse?: ChatResponse }
  | { type: "SET_STREAMING"; isStreaming: boolean }
  | { type: "SET_AGENT_PROGRESS"; step: number; agent: string }
  | { type: "SET_LATEST_RESPONSE"; response: ChatResponse }
  | { type: "CLEAR_PROGRESS" }
  | { type: "SET_MODE"; mode: AppMode }
  | { type: "SET_COLLECTIONS"; collections: STACCollection[] }
  | { type: "SET_DRAWN_BBOX"; bbox: number[] | null }
  | { type: "SET_EXPLORER_RESULTS"; results: STACFeatureCollection | null }
  | { type: "SET_SELECTED_ITEM"; item: STACFeature | null }
  | { type: "SET_ACTIVE_TILE_LAYER"; config: TileLayerConfig | null }
  | { type: "SET_EXPLORER_LOADING"; loading: boolean }
  | { type: "SET_EXPLORER_ERROR"; error: string | null };

const initialState: AppState = {
  mode: "chat",
  messages: [],
  isStreaming: false,
  currentStep: null,
  currentAgent: null,
  latestResponse: null,
  collections: [],
  drawnBbox: null,
  explorerResults: null,
  selectedItem: null,
  activeTileLayer: null,
  explorerLoading: false,
  explorerError: null,
};

function reducer(state: AppState, action: Action): AppState {
  switch (action.type) {
    case "ADD_MESSAGE":
      return { ...state, messages: [...state.messages, action.message] };
    case "UPDATE_LAST_ASSISTANT": {
      const msgs = [...state.messages];
      const lastIdx = msgs.findLastIndex((m) => m.role === "assistant");
      if (lastIdx >= 0) {
        msgs[lastIdx] = {
          ...msgs[lastIdx],
          content: action.content,
          chatResponse: action.chatResponse ?? msgs[lastIdx].chatResponse,
        };
      }
      return { ...state, messages: msgs };
    }
    case "SET_STREAMING":
      return { ...state, isStreaming: action.isStreaming };
    case "SET_AGENT_PROGRESS":
      return { ...state, currentStep: action.step, currentAgent: action.agent };
    case "SET_LATEST_RESPONSE":
      return { ...state, latestResponse: action.response };
    case "CLEAR_PROGRESS":
      return { ...state, currentStep: null, currentAgent: null };
    case "SET_MODE":
      return { ...state, mode: action.mode };
    case "SET_COLLECTIONS":
      return { ...state, collections: action.collections };
    case "SET_DRAWN_BBOX":
      return { ...state, drawnBbox: action.bbox };
    case "SET_EXPLORER_RESULTS":
      return { ...state, explorerResults: action.results };
    case "SET_SELECTED_ITEM":
      return { ...state, selectedItem: action.item };
    case "SET_ACTIVE_TILE_LAYER":
      return { ...state, activeTileLayer: action.config };
    case "SET_EXPLORER_LOADING":
      return { ...state, explorerLoading: action.loading };
    case "SET_EXPLORER_ERROR":
      return { ...state, explorerError: action.error };
    default:
      return state;
  }
}

const AppContext = createContext<AppState>(initialState);
const DispatchContext = createContext<Dispatch<Action>>(() => {});

export function AppProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(reducer, initialState);
  return (
    <AppContext.Provider value={state}>
      <DispatchContext.Provider value={dispatch}>{children}</DispatchContext.Provider>
    </AppContext.Provider>
  );
}

export function useAppState() {
  return useContext(AppContext);
}

export function useAppDispatch() {
  return useContext(DispatchContext);
}
