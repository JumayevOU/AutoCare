import math
from typing import Optional, List, Dict, Any
from aiogram.types import Location
from utils.misc import show_on_gmaps
from data.locations import Autoservice, CarWash
import logging

logger = logging.getLogger(__name__)

def calc_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000  # Yer radiusi metrlarda
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return (R * c) / 1000.0  # km ga aylantirish


def choose_shortest(
    location: Location | dict,
    max_results: Optional[int] = 10,
    place_type: str = "autoservice"
) -> List[Dict[str, Any]]:
    logger.debug(f"choose_shortest chaqirildi: place_type={place_type}, max_results={max_results}")
    
    if isinstance(location, Location):
        user_lat = location.latitude
        user_lon = location.longitude
    elif isinstance(location, dict):
        user_lat = float(location.get('latitude') or location.get('lat', 0))
        user_lon = float(location.get('longitude') or location.get('lon', 0))
        
        if user_lat == 0 or user_lon == 0:
            raise ValueError("Noto'g'ri koordinata formatida")
    else:
        raise ValueError("Location format not supported. Use aiogram.types.Location or dict with 'latitude'/'longitude'")

    logger.debug(f"Foydalanuvchi koordinatalari: lat={user_lat}, lon={user_lon}")

    if place_type == "carwash":
        places = CarWash
        logger.debug(f"CarWash dan {len(places)} ta joy mavjud")
    else:
        places = Autoservice
        logger.debug(f"Autoservice dan {len(places)} ta joy mavjud")

    results: List[Dict[str, Any]] = []

    for place in places:
        try:
            lat2 = float(place.get("lat") or place.get("latitude", 0))
            lon2 = float(place.get("lon") or place.get("longitude", 0))
            
            if lat2 == 0 or lon2 == 0:
                logger.warning(f"Joy {place.get('name')} da noto'g'ri koordinata: lat={lat2}, lon={lon2}")
                continue
                
        except (ValueError, TypeError) as e:
            logger.error(f"Joy {place.get('name')} koordinatasini o'qishda xato: {e}")
            continue

        dist_km = calc_distance(user_lat, user_lon, lat2, lon2)
        logger.debug(f"Joy {place.get('name')}: {dist_km:.2f} km")

        try:
            gmaps_url = show_on_gmaps.show(lat=lat2, lon=lon2)
        except (AttributeError, ImportError, Exception) as e:
            logger.warning(f"GMaps URL yaratishda xato: {e}")
            gmaps_url = f"https://www.google.com/maps?q={lat2},{lon2}"

        place_data = {
            "id": place.get("id") or f"{place_type}_{len(results)}",
            "name": place.get("name", "Noma'lum joy"),
            "distance_km": round(dist_km, 2),  # 2 xona aniqlikda
            "address": place.get("address", "Manzil yo'q"),
            "phone": place.get("phone", ""),
            "lat": lat2,
            "lon": lon2,
            "services": place.get("services", []),
            "working_days": place.get("working_days", []),
            "working_hours": place.get("working_hours", {}),
            "is_24_7": bool(place.get("is_24_7", False)),
            "gmaps_url": gmaps_url,
        }
        
        if "description" in place:
            place_data["description"] = place.get("description")
        if "rating" in place:
            place_data["rating"] = place.get("rating")
        if "image_url" in place:
            place_data["image_url"] = place.get("image_url")

        results.append(place_data)
        logger.debug(f"Joy {place.get('name')} qo'shildi")

    results.sort(key=lambda x: x["distance_km"])
    logger.debug(f"Jami {len(results)} ta joy topildi va masofa bo'yicha tartiblandi")

    if max_results is None:
        return results
    return results[:max_results]



def filter_places_by_service(
    places: List[Dict[str, Any]], 
    service_filter: str,
    case_sensitive: bool = False
) -> List[Dict[str, Any]]:
    if not service_filter:
        return places
        
    filtered_places = []
    search_term = service_filter if case_sensitive else service_filter.lower()
    
    for place in places:
        services = place.get("services", [])
        for service in services:
            service_name = service if case_sensitive else service.lower()
            if search_term in service_name:
                filtered_places.append(place)
                break
                
    return filtered_places


def get_places_in_radius(
    location: Location | dict,
    radius_km: float = 5.0,
    place_type: str = "autoservice"
) -> List[Dict[str, Any]]:
    all_places = choose_shortest(location, max_results=None, place_type=place_type)
    return [place for place in all_places if place["distance_km"] <= radius_km]


def format_distance(distance_km: float) -> str:
    if distance_km < 1:
        return f"{int(distance_km * 1000)} m"
    elif distance_km < 10:
        return f"{distance_km:.1f} km"
    else:
        return f"{int(distance_km)} km"


def validate_place_data(place: Dict[str, Any]) -> bool:
    required_fields = ["name", "lat", "lon"]
    
    for field in required_fields:
        if field not in place or not place[field]:
            return False
            
    try:
        lat = float(place["lat"])
        lon = float(place["lon"])
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            return False
    except (ValueError, TypeError):
        return False
        
    return True