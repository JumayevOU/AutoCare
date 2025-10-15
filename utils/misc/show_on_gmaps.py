from typing import Optional, Union, Dict, Any
from aiogram import types

URL = "https://maps.google.com/maps?q={lat},{lon}"


def show(lat: Optional[Union[float, str]] = None,
         lon: Optional[Union[float, str]] = None,
         location: Optional[Union[types.Location, Dict[str, Any]]] = None) -> str:
    if location is not None:
        if isinstance(location, types.Location):
            lat = location.latitude
            lon = location.longitude
        elif isinstance(location, dict):
            lat = location.get("lat") or location.get("latitude")
            lon = location.get("lon") or location.get("longitude")

    if lat is None or lon is None:
        raise ValueError("lat va lon qiymatlari yoki location obyekti berilishi kerak.")

    try:
        lat_f = float(lat)
        lon_f = float(lon)
    except Exception as e:
        raise ValueError(f"lat yoki lon son bo'lishi kerak: {e}")

    return URL.format(lat=lat_f, lon=lon_f)
