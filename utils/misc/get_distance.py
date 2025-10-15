# utils/misc/get_distance.py
import math
from typing import Optional, List, Dict, Any, Union
from aiogram.types import Location
from database import get_nearby_places
import logging

logger = logging.getLogger(__name__)

async def choose_shortest(
    location: Union[Location, dict],
    max_results: Optional[int] = 10,
    place_type: str = "autoservice"
) -> List[Dict[str, Any]]:
    """
    Database dan eng yaqin joylarni topish
    """
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

    try:
        # Database dan ma'lumot olish
        places = await get_nearby_places(
            user_lat, 
            user_lon, 
            radius_km=50.0,
            place_type=place_type
        )
        
        if not places:
            logger.debug("Database dan hech qanday joy topilmadi")
            return []
        
        # Kerakli formatga o'tkazish
        results = []
        for place in places[:max_results]:
            # Google Maps URL yaratish
            gmaps_url = f"https://maps.google.com/?q={place['lat']},{place['lon']}"
            
            results.append({
                "id": place["id"],
                "name": place["name"],
                "distance_km": round(place["distance_km"], 2),
                "address": place["address"],
                "phone": place["phone"],
                "lat": place["lat"],
                "lon": place["lon"],
                "services": place["services"],
                "working_days": place["working_days"],
                "working_hours": place["working_hours"],
                "is_24_7": place["is_24_7"],
                "gmaps_url": gmaps_url
            })
        
        logger.debug(f"Jami {len(results)} ta joy topildi")
        return results
        
    except Exception as e:
        logger.error(f"Database dan ma'lumot olishda xatolik: {e}")
        return []

def calc_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Ikkita nuqta orasidagi masofani hisoblash (km)
    """
    R = 6371  # Yer radiusi km da
    
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
         math.sin(dlon / 2) * math.sin(dlon / 2))
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def format_distance(distance_km: float) -> str:
    """
    Masofani formatlash
    """
    if distance_km < 1:
        return f"{int(distance_km * 1000)} m"
    elif distance_km < 10:
        return f"{distance_km:.1f} km"
    else:
        return f"{int(distance_km)} km"
