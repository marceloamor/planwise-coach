/**
 * Anonymous client ID management for the AI Run Coach.
 * Generates a unique ID per device/browser and persists it in localStorage.
 */

export function getAnonId(): string {
  // Return placeholder for SSR
  if (typeof window === "undefined") return "ssr-placeholder";
  
  const storageKey = "anon_client_id";
  let clientId = localStorage.getItem(storageKey);
  
  if (!clientId) {
    // Generate a new UUID-like ID
    clientId = crypto.randomUUID();
    localStorage.setItem(storageKey, clientId);
  }
  
  return clientId;
}

export function resetAnonId(): string {
  if (typeof window === "undefined") return "ssr-placeholder";
  
  const storageKey = "anon_client_id";
  const newId = crypto.randomUUID();
  localStorage.setItem(storageKey, newId);
  return newId;
} 