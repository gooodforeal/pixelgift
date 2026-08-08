import { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

import {
  DEFAULT_GEOPOINT,
  type GeopointCoords,
} from "../lib/geopoint";

const MARKER_ICON = L.icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

interface MapPointPickerProps {
  value: GeopointCoords | null;
  onChange: (coords: GeopointCoords) => void;
  disabled?: boolean;
  className?: string;
}

export function MapPointPicker({
  value,
  onChange,
  disabled = false,
  className = "",
}: MapPointPickerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<L.Map | null>(null);
  const markerRef = useRef<L.Marker | null>(null);
  const onChangeRef = useRef(onChange);
  onChangeRef.current = onChange;

  useEffect(() => {
    const el = containerRef.current;
    if (!el || mapRef.current) return;

    const start = value ?? DEFAULT_GEOPOINT;
    const map = L.map(el, {
      center: [start.lat, start.lng],
      zoom: 13,
      scrollWheelZoom: true,
    });

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      attribution:
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      maxZoom: 19,
    }).addTo(map);

    const marker = L.marker([start.lat, start.lng], {
      icon: MARKER_ICON,
      draggable: !disabled,
    }).addTo(map);
    markerRef.current = marker;

    const emit = (lat: number, lng: number) => {
      onChangeRef.current({
        lat: Math.round(lat * 1e6) / 1e6,
        lng: Math.round(lng * 1e6) / 1e6,
      });
    };

    if (!value) emit(start.lat, start.lng);

    map.on("click", (event: L.LeafletMouseEvent) => {
      if (disabled) return;
      const { lat, lng } = event.latlng;
      marker.setLatLng([lat, lng]);
      emit(lat, lng);
    });

    marker.on("dragend", () => {
      if (disabled) return;
      const { lat, lng } = marker.getLatLng();
      emit(lat, lng);
    });

    mapRef.current = map;

    // Leaflet needs a layout pass after mount in flex/hidden containers.
    requestAnimationFrame(() => map.invalidateSize());

    return () => {
      map.remove();
      mapRef.current = null;
      markerRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps -- init once
  }, []);

  useEffect(() => {
    const map = mapRef.current;
    const marker = markerRef.current;
    if (!map || !marker || !value) return;
    const current = marker.getLatLng();
    if (
      Math.abs(current.lat - value.lat) > 1e-6 ||
      Math.abs(current.lng - value.lng) > 1e-6
    ) {
      marker.setLatLng([value.lat, value.lng]);
      map.panTo([value.lat, value.lng]);
    }
  }, [value]);

  useEffect(() => {
    const marker = markerRef.current;
    if (!marker) return;
    if (disabled) marker.dragging?.disable();
    else marker.dragging?.enable();
  }, [disabled]);

  return (
    <div
      ref={containerRef}
      className={`z-0 h-56 w-full overflow-hidden rounded-2xl border border-white/12 sm:h-64 ${className}`}
      aria-label="Карта для выбора точки"
    />
  );
}
