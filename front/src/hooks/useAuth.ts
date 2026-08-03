import { useSyncExternalStore } from "react";

import { api } from "../lib/api";
import { isAuthed, setAuthed, subscribeAuth } from "../lib/auth";

export function useAuth() {
  const authenticated = useSyncExternalStore(subscribeAuth, isAuthed, () => false);

  return {
    isAuthenticated: authenticated,
    login: () => setAuthed(true),
    logout: async () => {
      try {
        await api.logout();
      } catch {
        /* cookie may already be gone */
      }
      setAuthed(false);
    },
  };
}
