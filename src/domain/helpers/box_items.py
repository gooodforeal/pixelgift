from typing import Any


def parse_geopoint_metadata(metadata: dict[str, Any] | None) -> tuple[float, float]:
    data = metadata or {}
    lat = data.get("lat")
    lng = data.get("lng")
    if not isinstance(lat, (int, float)) or isinstance(lat, bool):
        raise ValueError("Geopoint item requires numeric metadata.lat")
    if not isinstance(lng, (int, float)) or isinstance(lng, bool):
        raise ValueError("Geopoint item requires numeric metadata.lng")
    lat_f = float(lat)
    lng_f = float(lng)
    if not (-90.0 <= lat_f <= 90.0):
        raise ValueError("metadata.lat must be between -90 and 90")
    if not (-180.0 <= lng_f <= 180.0):
        raise ValueError("metadata.lng must be between -180 and 180")
    return lat_f, lng_f
