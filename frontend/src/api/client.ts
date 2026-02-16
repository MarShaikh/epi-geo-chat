/** Fetch wrapper for the backend REST API. */

const API_BASE = "/api/v1";

export async function postChat(query: string): Promise<Response> {
  return fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query }),
  });
}

export async function checkHealth(): Promise<{ status: string }> {
  const res = await fetch("/health");
  return res.json();
}
