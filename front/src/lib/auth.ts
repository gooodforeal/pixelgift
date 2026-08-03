const AUTH_KEY = "pixelgift.authed";

type Listener = (authed: boolean) => void;

const listeners = new Set<Listener>();

function readAuthed(): boolean {
  try {
    return sessionStorage.getItem(AUTH_KEY) === "1";
  } catch {
    return false;
  }
}

export function isAuthed(): boolean {
  return readAuthed();
}

export function setAuthed(value: boolean): void {
  try {
    if (value) sessionStorage.setItem(AUTH_KEY, "1");
    else sessionStorage.removeItem(AUTH_KEY);
    // Migrate away from legacy JWT in localStorage.
    localStorage.removeItem("pixelgift.token");
  } catch {
    /* storage unavailable */
  }
  listeners.forEach((listener) => listener(value));
}

export function subscribeAuth(listener: Listener): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}
