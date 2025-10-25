import json
import logging
from typing import Dict, Any, List
from .connection import get_pool
from .models import REQUIRED_FIELDS
from .queries import QUERIES

logger = logging.getLogger(__name__)

async def insert_autoservice(data: Dict[str, Any]) -> bool:
    """Insert or update an autoservice in the database."""
    return await _insert_place(data, "autoservice")

async def insert_carwash(data: Dict[str, Any]) -> bool:
    """Insert or update a carwash in the database."""
    return await _insert_place(data, "carwash")

async def _insert_place(data: Dict[str, Any], place_type: str) -> bool:
    """
    Generic function to insert or update a place (autoservice/carwash).
    
    Args:
        data: Dictionary containing place information
        place_type: Type of place ("autoservice" or "carwash")
        
    Returns:
        bool: True if successful, False otherwise.
    """
    pool = get_pool()
    if pool is None:
        from .connection import init_db
        await init_db()
        pool = get_pool()
    
    # Validate required fields
    required_fields = REQUIRED_FIELDS.get(place_type, [])
    for field in required_fields:
        if field not in data:
            logger.error(f"❌ Missing required field: {field}")
            return False
    
    query = QUERIES[f"insert_{place_type}"]
    
    try:
        async with pool.acquire() as conn: # pyright: ignore[reportOptionalMemberAccess]
            await conn.execute(
                query,
                data["id"],
                data["name"],
                float(data["lat"]),
                float(data["lon"]),
                data.get("address"),
                data.get("phone"),
                data.get("services", []),
                data.get("working_days", []),
                data.get("working_hours", {}),
                bool(data.get("is_24_7", False)),
            )
            return True
    except Exception as e:
        logger.error(f"❌ Error inserting {place_type}: {e}")
        return False

async def get_all_autoservices() -> List[Dict[str, Any]]:
    """Retrieve all autoservices from the database."""
    return await _get_all_places("autoservice")

async def get_all_carwashes() -> List[Dict[str, Any]]:
    """Retrieve all carwashes from the database."""
    return await _get_all_places("carwash")

async def _get_all_places(place_type: str) -> List[Dict[str, Any]]:
    """Generic function to retrieve all places of a specific type."""
    pool = get_pool()
    if pool is None:
        from .connection import init_db
        await init_db()
        pool = get_pool()
    
    query = f"SELECT * FROM {place_type}"
    try:
        async with pool.acquire() as conn:  # pyright: ignore[reportOptionalMemberAccess]
            rows = await conn.fetch(query)
            return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"❌ Error fetching {place_type}s: {e}")
        return []

async def get_nearby_places(lat: float, lon: float, radius_km: float = 50.0, place_type: str = "autoservice") -> List[Dict[str, Any]]:
    """
    Find nearby places within a specified radius using Haversine formula.
    
    Args:
        lat: User's latitude
        lon: User's longitude
        radius_km: Search radius in kilometers (default: 50.0)
        place_type: Type of place to search ("autoservice" or "carwash")
        
    Returns:
        List[Dict[str, Any]]: List of nearby places sorted by distance.
    """
    pool = get_pool()
    if pool is None:
        from .connection import init_db
        await init_db()
        pool = get_pool()
        if pool is None:
            logger.error("❌ Database pool not initialized")
            return []
    
    # Validate inputs
    if place_type not in ("autoservice", "carwash"):
        logger.error(f"❌ Invalid place_type: {place_type}")
        raise ValueError(f"Invalid place_type: {place_type}. Must be 'autoservice' or 'carwash'")
    
    if not (-90 <= lat <= 90):
        logger.error("❌ Invalid latitude provided")
        raise ValueError(f"Invalid latitude. Must be between -90 and 90")
    if not (-180 <= lon <= 180):
        logger.error("❌ Invalid longitude provided")
        raise ValueError(f"Invalid longitude. Must be between -180 and 180")
    
    query = QUERIES["nearby_places"].format(table=place_type)
    
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, lat, lon, radius_km)
            return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"❌ Error finding nearby places: {e}")
        return []

async def search_places_by_service(service_name: str, place_type: str = "autoservice") -> List[Dict[str, Any]]:
    """Search places by service name."""
    if place_type not in ("autoservice", "carwash"):
        logger.error(f"❌ Invalid place_type: {place_type}")
        raise ValueError(f"Invalid place_type: {place_type}. Must be 'autoservice' or 'carwash'")
    
    query = f"SELECT * FROM {place_type} WHERE services @> $1::jsonb"
    pool = get_pool()
    try:
        async with pool.acquire() as conn:  # pyright: ignore[reportOptionalMemberAccess]
            rows = await conn.fetch(query, json.dumps([service_name]))
            return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"❌ Error searching by service: {e}")
        return []

async def batch_insert_autoservices(services_data: List[Dict[str, Any]]) -> bool:
    """Insert multiple autoservices in a single transaction."""
    return await _batch_insert(services_data, "autoservice")

async def batch_insert_carwashes(carwashes_data: List[Dict[str, Any]]) -> bool:
    """Insert multiple carwashes in a single transaction."""
    return await _batch_insert(carwashes_data, "carwash")

async def _batch_insert(data_list: List[Dict[str, Any]], place_type: str) -> bool:
    """Generic batch insert function."""
    pool = get_pool()
    try:
        async with pool.acquire() as conn:  # pyright: ignore[reportOptionalMemberAccess]
            async with conn.transaction():
                insert_func = insert_autoservice if place_type == "autoservice" else insert_carwash
                for data in data_list:
                    await insert_func(data)
        return True
    except Exception as e:
        logger.error(f"❌ Batch insert error: {e}")
        return False