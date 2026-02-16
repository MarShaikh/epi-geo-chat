import { useCallback, useRef } from "react";
import { useAppDispatch, useAppState } from "../context/AppContext";
import { streamChat } from "../api/stream";
import type { ChatResponse, StreamEvent } from "../types/api";

const AGENT_LABELS: Record<string, string> = {
  query_parser: "Parsing query",
  geocoding: "Resolving location & time",
  stac_coordinator: "Searching STAC catalog",
  response_synthesizer: "Generating response",
};

export function useChat() {
  const dispatch = useAppDispatch();
  const { isStreaming } = useAppState();
  const abortRef = useRef<AbortController | null>(null);

  const sendQuery = useCallback(
    async (query: string) => {
      if (isStreaming) return;

      // Add user message
      dispatch({
        type: "ADD_MESSAGE",
        message: { id: crypto.randomUUID(), role: "user", content: query, timestamp: new Date() },
      });

      // Add placeholder assistant message
      dispatch({
        type: "ADD_MESSAGE",
        message: { id: crypto.randomUUID(), role: "assistant", content: "", timestamp: new Date() },
      });

      dispatch({ type: "SET_STREAMING", isStreaming: true });

      const controller = new AbortController();
      abortRef.current = controller;

      try {
        await streamChat(
          query,
          (event: StreamEvent) => {
            if (event.event === "agent_started" && event.agent && event.step) {
              dispatch({ type: "SET_AGENT_PROGRESS", step: event.step, agent: event.agent });
              const label = AGENT_LABELS[event.agent] ?? event.agent;
              dispatch({
                type: "UPDATE_LAST_ASSISTANT",
                content: `${label}...`,
              });
            }

            if (event.event === "agent_completed" && event.agent === "response_synthesizer") {
              const response = (event.data as Record<string, string>)?.response ?? "";
              dispatch({ type: "UPDATE_LAST_ASSISTANT", content: response });
            }

            if (event.event === "done" && event.data) {
              // Map WorkflowResult.to_dict() keys to ChatResponse keys
              const d = event.data as Record<string, unknown>;
              const chatResponse: ChatResponse = {
                query: d.user_query as string,
                parsed_query: d.parsed_query as ChatResponse["parsed_query"],
                geocoding: d.geocoding_result as ChatResponse["geocoding"],
                stac_results: d.stac_results as ChatResponse["stac_results"],
                response: d.final_response as string,
                trace_id: null,
              };
              dispatch({ type: "SET_LATEST_RESPONSE", response: chatResponse });
              dispatch({
                type: "UPDATE_LAST_ASSISTANT",
                content: chatResponse.response,
                chatResponse,
              });
            }

            if (event.event === "error") {
              dispatch({
                type: "UPDATE_LAST_ASSISTANT",
                content: `Error: ${event.message ?? "Something went wrong"}`,
              });
            }
          },
          (error: Error) => {
            dispatch({
              type: "UPDATE_LAST_ASSISTANT",
              content: `Error: ${error.message}`,
            });
          },
          controller.signal,
        );
      } finally {
        dispatch({ type: "SET_STREAMING", isStreaming: false });
        dispatch({ type: "CLEAR_PROGRESS" });
        abortRef.current = null;
      }
    },
    [dispatch, isStreaming],
  );

  const cancelQuery = useCallback(() => {
    abortRef.current?.abort();
  }, []);

  return { sendQuery, cancelQuery };
}
