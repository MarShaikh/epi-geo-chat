/** SSE stream handler for the /chat/stream endpoint. */

import { fetchEventSource } from "@microsoft/fetch-event-source";
import type { StreamEvent } from "../types/api";

const API_BASE = "/api/v1";

export async function streamChat(
  query: string,
  onEvent: (event: StreamEvent) => void,
  onError: (error: Error) => void,
  signal?: AbortSignal,
): Promise<void> {
  await fetchEventSource(`${API_BASE}/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
    signal,
    onmessage(msg) {
      if (msg.data) {
        const event: StreamEvent = JSON.parse(msg.data);
        onEvent(event);
      }
    },
    onerror(err) {
      onError(err instanceof Error ? err : new Error(String(err)));
      throw err; // stop retrying
    },
  });
}
