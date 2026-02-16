/** Mirrors backend Pydantic models from src/agents/ and src/api/schemas.py */

export interface ChatRequest {
  query: string;
  session_id?: string;
}

export interface ParsedQuery {
  intent: string;
  metadata_sub_intent: string | null;
  data_type_keywords: string[];
  location: string | null;
  datetime: string | null;
  additional_params: string | null;
}

export interface GeocodingResult {
  bbox: number[] | null; // [min_lon, min_lat, max_lon, max_lat]
  datetime: string | null;
  location_source: string | null;
}

export interface STACItem {
  id: string;
  datetime: string;
  assets: string[];
}

export interface STACSearchResult {
  count: number | null;
  collections: string[];
  date_range: string;
  items: STACItem[] | null;
  bbox_searched: number[] | null;
  description: string | null;
  keywords: string[] | null;
  license: string | null;
}

export interface ChatResponse {
  query: string;
  parsed_query: ParsedQuery;
  geocoding: GeocodingResult;
  stac_results: STACSearchResult;
  response: string;
  trace_id: string | null;
}

export interface StreamEvent {
  event: "agent_started" | "agent_completed" | "error" | "done";
  agent?: string;
  step?: number;
  data?: Record<string, unknown>;
  message?: string;
}

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  chatResponse?: ChatResponse;
}
