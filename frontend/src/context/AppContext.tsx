import { createContext, useContext, useReducer, type ReactNode, type Dispatch } from "react";
import type { ChatResponse, Message } from "../types/api";

/** Application state */
export interface AppState {
  messages: Message[];
  isStreaming: boolean;
  currentStep: number | null;
  currentAgent: string | null;
  latestResponse: ChatResponse | null;
}

/** Actions */
type Action =
  | { type: "ADD_MESSAGE"; message: Message }
  | { type: "UPDATE_LAST_ASSISTANT"; content: string; chatResponse?: ChatResponse }
  | { type: "SET_STREAMING"; isStreaming: boolean }
  | { type: "SET_AGENT_PROGRESS"; step: number; agent: string }
  | { type: "SET_LATEST_RESPONSE"; response: ChatResponse }
  | { type: "CLEAR_PROGRESS" };

const initialState: AppState = {
  messages: [],
  isStreaming: false,
  currentStep: null,
  currentAgent: null,
  latestResponse: null,
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
