import math
from datetime import datetime
from typing import Optional, Tuple, Dict, Any

def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Computes accurate Great Circle distance in meters between two GPS coordinates using the Haversine formula.
    """
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return 999999.0
        
    try:
        lat1, lon1, lat2, lon2 = float(lat1), float(lon1), float(lat2), float(lon2)
    except (ValueError, TypeError):
        return 999999.0

    R = 6371000.0  # Earth radius in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (math.sin(delta_phi / 2.0) ** 2 +
         math.cos(phi1) * math.cos(phi2) *
         math.sin(delta_lambda / 2.0) ** 2)
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c


def calculate_location_similarity(
    lat1: Optional[float], lon1: Optional[float], ward1: Optional[str],
    lat2: Optional[float], lon2: Optional[float], ward2: Optional[str],
    max_distance_meters: float = 150.0
) -> Tuple[float, float, str]:
    """
    Calculates spatial compatibility score (0.0 to 1.0) and distance in meters.
    Returns: (location_similarity_score, distance_meters, justification)
    """
    # 1. Coordinate-based evaluation
    if lat1 is not None and lon1 is not None and lat2 is not None and lon2 is not None:
        dist_m = haversine_distance_meters(lat1, lon1, lat2, lon2)
        if dist_m <= 25.0:
            return 1.0, dist_m, f"Immediate same-spot proximity ({dist_m:.1f}m)"
        elif dist_m <= 75.0:
            score = 1.0 - ((dist_m - 25.0) / 100.0) * 0.3
            return max(0.6, score), dist_m, f"Same street proximity ({dist_m:.1f}m)"
        elif dist_m <= max_distance_meters:
            score = 0.6 - ((dist_m - 75.0) / (max_distance_meters - 75.0)) * 0.4
            return max(0.2, score), dist_m, f"Within vicinity boundary ({dist_m:.1f}m)"
        else:
            return 0.0, dist_m, f"Geographically distant ({dist_m:.1f}m apart)"

    # 2. Ward-based fallback when coordinates are missing
    w1 = str(ward1).strip().lower() if ward1 else ""
    w2 = str(ward2).strip().lower() if ward2 else ""
    if w1 and w2:
        if w1 == w2:
            return 0.65, 100.0, f"Same municipal ward ({w1})"
        else:
            return 0.1, 5000.0, f"Different municipal wards ({w1} vs {w2})"

    return 0.3, 999999.0, "Missing location coordinates and ward info"


def calculate_temporal_compatibility(
    dt1_str: Optional[str],
    dt2_str: Optional[str],
    max_window_hours: float = 72.0
) -> Tuple[float, float, str]:
    """
    Computes temporal compatibility score (0.0 to 1.0) and time delta in hours.
    Returns: (temporal_score, delta_hours, justification)
    """
    if not dt1_str or not dt2_str:
        return 0.5, 0.0, "Timestamp missing, neutral temporal factor"

    def parse_dt(s):
        for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
            try:
                return datetime.strptime(s.replace("+00:00", "Z"), fmt)
            except ValueError:
                pass
        return None

    t1 = parse_dt(str(dt1_str))
    t2 = parse_dt(str(dt2_str))

    if not t1 or not t2:
        return 0.5, 0.0, "Unparseable timestamp, neutral factor"

    delta_hours = abs((t2 - t1).total_seconds()) / 3600.0

    if delta_hours <= 4.0:
        return 1.0, delta_hours, f"Reported almost simultaneously ({delta_hours:.1f}h window)"
    elif delta_hours <= 24.0:
        return 0.85, delta_hours, f"Reported within same working day ({delta_hours:.1f}h window)"
    elif delta_hours <= max_window_hours:
        score = 0.85 - ((delta_hours - 24.0) / (max_window_hours - 24.0)) * 0.5
        return max(0.2, score), delta_hours, f"Reported within active incident window ({delta_hours:.1f}h)"
    else:
        # Long gap suggests distinct or recurring events
        return 0.05, delta_hours, f"Large time gap ({delta_hours:.1f}h > {max_window_hours}h)"
