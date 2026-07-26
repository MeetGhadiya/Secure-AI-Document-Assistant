import { useEffect, useState } from "react";

const SESSION_KEY = "secure_rag_session_id";

function generateUUID() {
  if (crypto.randomUUID) return crypto.randomUUID();
  // Fallback UUID v4 generator for older browsers.
  return "10000000-1000-4000-8000-100000000000".replace(/[018]/g, (c) =>
    (c ^ (crypto.getRandomValues(new Uint8Array(1))[0] & (15 >> (c / 4)))).toString(16)
  );
}

/**
 * Every browser gets its own persistent, random session id. This id is
 * attached to every API request and is the mechanism that keeps one user's
 * documents isolated from another's -- the backend filters all vector
 * search and document lookups by this value.
 */
export function useSession() {
  const [sessionId, setSessionId] = useState(null);

  useEffect(() => {
    let existing = localStorage.getItem(SESSION_KEY);
    if (!existing) {
      existing = generateUUID();
      localStorage.setItem(SESSION_KEY, existing);
    }
    setSessionId(existing);
  }, []);

  return sessionId;
}
