export interface GeopointCoords {
  lat: number;
  lng: number;
  label?: string;
}

/** Default map center (Moscow). */
export const DEFAULT_GEOPOINT: GeopointCoords = {
  lat: 55.7558,
  lng: 37.6173,
};

export function geopointFromMetadata(
  metadata: Record<string, unknown> | null | undefined,
): GeopointCoords | null {
  const lat = metadata?.lat;
  const lng = metadata?.lng;
  if (typeof lat !== "number" || typeof lng !== "number") return null;
  if (!Number.isFinite(lat) || !Number.isFinite(lng)) return null;
  if (lat < -90 || lat > 90 || lng < -180 || lng > 180) return null;
  const label = metadata?.label;
  return {
    lat,
    lng,
    label: typeof label === "string" && label.trim() ? label.trim() : undefined,
  };
}

export function formatGeopointCoords(coords: GeopointCoords): string {
  return `${coords.lat.toFixed(5)}, ${coords.lng.toFixed(5)}`;
}

/** OpenStreetMap link for external navigation. */
export function osmMapUrl(coords: GeopointCoords, zoom = 16): string {
  return `https://www.openstreetmap.org/?mlat=${coords.lat}&mlon=${coords.lng}#map=${zoom}/${coords.lat}/${coords.lng}`;
}
