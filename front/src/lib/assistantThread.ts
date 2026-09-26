const THREAD_STORAGE_KEY = "pixelgift:assistant-thread-id";

export function getOrCreateAssistantThreadId(): string {
  try {
    const existing = sessionStorage.getItem(THREAD_STORAGE_KEY);
    if (existing) return existing;
    const created = crypto.randomUUID();
    sessionStorage.setItem(THREAD_STORAGE_KEY, created);
    return created;
  } catch {
    return crypto.randomUUID();
  }
}

export function clearAssistantThreadId(): void {
  try {
    sessionStorage.removeItem(THREAD_STORAGE_KEY);
  } catch {
    // ignore quota / private mode
  }
}
