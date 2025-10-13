import math
from typing import Optional, List, Dict, Any
from aiogram import types
from utils.misc import show_on_gmaps
from data.locations import Autoservice, CarWash


def calc_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Haversine formulasi bilan masofani km da hisoblaydi."""
    R = 6371000  
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return (R * c) / 1000.0  # km


def choose_shortest(
    location: types.Location | dict,
    max_results: Optional[int] = 10,
    place_type: str = "autoservice"
) -> List[Dict[str, Any]]:
    """
    location: aiogram.types.Location yoki {'lat':..., 'lon':...}
    place_type: 'autoservice' yoki 'carwash'
    max_results: nechta natija qaytarilsin
    """
    if hasattr(location, "latitude") and hasattr(location, "longitude"):
        user_lat = float(location.latitude)
        user_lon = float(location.longitude)
    elif isinstance(location, dict):
        user_lat = float(location.get("lat") or location.get("latitude"))
        user_lon = float(location.get("lon") or location.get("longitude"))
    else:
        raise ValueError("Location format not supported. Use message.location or {'lat','lon'} dict.")

    if place_type == "carwash":
        places = CarWash
    else:
        places = Autoservice

    results: List[Dict[str, Any]] = []

    for place in places:
        try:
            lat2 = float(place.get("lat"))
            lon2 = float(place.get("lon"))
        except Exception:
            continue

        dist_km = calc_distance(user_lat, user_lon, lat2, lon2)

        try:
            gmaps_url = show_on_gmaps.show(lat=lat2, lon=lon2)
        except Exception:
            gmaps_url = None

        results.append({
            "id": place.get("id"),
            "name": place.get("name", "Noma'lum joy"),
            "distance_km": dist_km,
            "address": place.get("address", "Manzil yo'q"),
            "phone": place.get("phone", ""),
            "lat": lat2,
            "lon": lon2,
            "services": place.get("services", []),
            "working_days": place.get("working_days", []),
            "working_hours": place.get("working_hours", {}),
            "is_24_7": bool(place.get("is_24_7", False)),
            "gmaps_url": gmaps_url,
        })

    results.sort(key=lambda x: x["distance_km"])

    if not max_results:
        return results
    return results[:max_results]
