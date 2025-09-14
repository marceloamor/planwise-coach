/**
 * API client for the AI Run Coach backend.
 * Handles communication with FastAPI endpoints.
 */

export const API_BASE = process.env.NEXT_PUBLIC_API_BASE ?? "http://localhost:8000";

export interface ChatMessage {
  client_id: string;
  message: string;
}

export interface ChatResponse {
  reply: string;
  plan_updated: boolean;
  plan?: PlanDoc | null;
}

export interface PlanResponse {
  plan?: PlanDoc | null;
  version?: number | null;
  created_at?: string | null;
}

// Plan type definitions (matching backend schemas)
export interface Session {
  date?: string | null;
  type: string;
  distance_km?: number | null;
  time_min?: number | null;
  intensity?: string | null;
  rpe?: number | null;
  structure?: string | null;
  notes?: string | null;
  day_of_week?: string | null;
  is_rest_day?: boolean | null;
}

export interface WeekPlan {
  mileage_target?: number | null;
  sessions: Session[];
}

export interface PlanMeta {
  goal?: string | null;
  race_date?: string | null;
  phase?: string | null;
  weekly_km_target?: number | null;
}

export interface PlanConstraints {
  max_weekly_increase_pct?: number | null;
  min_rest_days?: number | null;
}

export interface PlanDoc {
  meta: PlanMeta;
  constraints?: PlanConstraints | null;
  weeks: Record<string, WeekPlan>;
}

/**
 * Fetch the current plan for a client
 */
export async function fetchPlan(clientId: string): Promise<PlanResponse> {
  const url = new URL(`${API_BASE}/plan`);
  url.searchParams.set("client_id", clientId);
  
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to fetch plan: ${response.status} ${response.statusText}`);
  }
  
  return response.json();
}

/**
 * Send a chat message and get a response with optional plan update
 */
export async function sendChat(clientId: string, message: string): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Client-Id": clientId,
    },
    body: JSON.stringify({
      client_id: clientId,
      message: message.trim(),
    }),
  });
  
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Chat failed: ${response.status} ${response.statusText}`);
  }
  
  return response.json();
}

/**
 * Reset/clear all data for a client session
 */
export async function resetSession(clientId: string): Promise<{success: boolean, message: string}> {
  const response = await fetch(`${API_BASE}/session/${clientId}`, {
    method: "DELETE",
  });
  
  if (!response.ok) {
    throw new Error(`Failed to reset session: ${response.status} ${response.statusText}`);
  }
  
  return response.json();
}

/**
 * Test backend connectivity
 */
export async function healthCheck(): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE}/health`);
    return response.ok;
  } catch {
    return false;
  }
} 