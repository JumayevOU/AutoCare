# database.py
"""
Database module for AutoCare bot.

Provides PostgreSQL database operations with connection pooling,
CRUD operations for autoservices and carwashes, and location-based queries.
"""
import os
import asyncio
import asyncpg
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")

# Connection pool ni global saqlaymiz
pool: Optional[asyncpg.Pool] = None

CREATE_TABLES_SQL = """
CREATE TABLE IF NOT EXISTS autoservice (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    lat DOUBLE PRECISION NOT NULL,
    lon DOUBLE PRECISION NOT NULL,
    address TEXT,
    phone TEXT,
    services JSONB,
    working_days INTEGER[],
    working_hours JSONB,
    is_24_7 BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE IF NOT EXISTS carwash (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    lat DOUBLE PRECISION NOT NULL,
    lon DOUBLE PRECISION NOT NULL,
    address TEXT,
    phone TEXT,
    services JSONB,
    working_days INTEGER[],
    working_hours JSONB,
    is_24_7 BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Indexlar qo'shamiz
CREATE INDEX IF NOT EXISTS idx_autoservice_coords ON autoservice(lat, lon);
CREATE INDEX IF NOT EXISTS idx_carwash_coords ON carwash(lat, lon);
CREATE INDEX IF NOT EXISTS idx_autoservice_services ON autoservice USING GIN(services);
CREATE INDEX IF NOT EXISTS idx_carwash_services ON carwash USING GIN(services);
"""

async def init_db(database_url: Optional[str] = None) -> None:
    """
    Initialize database and create connection pool.
    
    Args:
        database_url: PostgreSQL connection URL. If not provided, uses DATABASE_URL env var.
        
    Raises:
        ValueError: If database URL is not provided or invalid.
        asyncpg.PostgresError: If database connection or table creation fails.
    """
    global pool
    db_url = database_url or DATABASE_URL
    
    if not db_url:
        error_msg = "DATABASE_URL environment variable not found"
        logger.error(f"❌ {error_msg}")
        raise ValueError(error_msg)
    
    # Validate database URL format
    if not db_url.startswith(('postgresql://', 'postgres://')):
        error_msg = "Invalid DATABASE_URL format. Must start with postgresql:// or postgres://"
        logger.error(f"❌ {error_msg}")
        raise ValueError(error_msg)
    
    try:
        pool = await asyncpg.create_pool(
            db_url,
            min_size=1,
            max_size=10,
            command_timeout=60
        )
        
        async with pool.acquire() as conn:
            await conn.execute(CREATE_TABLES_SQL)
            logger.info("✅ Database tables created/verified successfully")
            
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}")
        pool = None
        raise

async def close_db() -> None:
    """Close database connection pool gracefully."""
    global pool
    if pool:
        await pool.close()
        pool = None
        logger.info("✅ Database connection pool closed")

async def get_connection() -> asyncpg.Connection:
    """
    Acquire a database connection from the pool.
    
    Returns:
        asyncpg.Connection: Database connection from the pool.
        
    Raises:
        RuntimeError: If database pool is not initialized.
    """
    global pool
    if pool is None:
        await init_db()
    if pool is None:
        raise RuntimeError("Failed to initialize database connection pool")
    return await pool.acquire()

async def release_connection(conn: asyncpg.Connection) -> None:
    """
    Release a connection back to the pool.
    
    Args:
        conn: Database connection to release.
    """
    if pool:
        await pool.release(conn)

# ================== CRUD OPERATIONLARI ==================

async def insert_autoservice(data: Dict[str, Any]) -> bool:
    """
    Insert or update an autoservice in the database.
    
    Args:
        data: Dictionary containing autoservice information with keys:
            - id: Unique identifier
            - name: Service name
            - lat: Latitude
            - lon: Longitude
            - address: Optional address
            - phone: Optional phone number
            - services: List of services offered
            - working_days: List of working day numbers (0-6)
            - working_hours: Dict with 'start' and 'end' times
            - is_24_7: Boolean for 24/7 operation
            
    Returns:
        bool: True if successful, False otherwise.
    """
    global pool
    if pool is None:
        await init_db()
    
    # Validate required fields
    required_fields = ['id', 'name', 'lat', 'lon']
    for field in required_fields:
        if field not in data:
            logger.error(f"❌ Missing required field: {field}")
            return False
    
    query = """
    INSERT INTO autoservice (
        id, name, lat, lon, address, phone, services, working_days, working_hours, is_24_7
    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
    ON CONFLICT (id) DO UPDATE SET
        name = EXCLUDED.name,
        lat = EXCLUDED.lat,
        lon = EXCLUDED.lon,
        address = EXCLUDED.address,
        phone = EXCLUDED.phone,
        services = EXCLUDED.services,
        working_days = EXCLUDED.working_days,
        working_hours = EXCLUDED.working_hours,
        is_24_7 = EXCLUDED.is_24_7,
        updated_at = now()
    """
    try:
        async with pool.acquire() as conn:
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
        logger.error(f"❌ Error inserting autoservice: {e}")
        return False

async def insert_carwash(data: Dict[str, Any]) -> bool:
    """
    Insert or update a carwash in the database.
    
    Args:
        data: Dictionary containing carwash information with keys:
            - id: Unique identifier
            - name: Carwash name
            - lat: Latitude
            - lon: Longitude
            - address: Optional address
            - phone: Optional phone number
            - services: List of services offered
            - working_days: List of working day numbers (0-6)
            - working_hours: Dict with 'start' and 'end' times
            - is_24_7: Boolean for 24/7 operation
            
    Returns:
        bool: True if successful, False otherwise.
    """
    global pool
    if pool is None:
        await init_db()
    
    # Validate required fields
    required_fields = ['id', 'name', 'lat', 'lon']
    for field in required_fields:
        if field not in data:
            logger.error(f"❌ Missing required field: {field}")
            return False
    
    query = """
    INSERT INTO carwash (
        id, name, lat, lon, address, phone, services, working_days, working_hours, is_24_7
    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
    ON CONFLICT (id) DO UPDATE SET
        name = EXCLUDED.name,
        lat = EXCLUDED.lat,
        lon = EXCLUDED.lon,
        address = EXCLUDED.address,
        phone = EXCLUDED.phone,
        services = EXCLUDED.services,
        working_days = EXCLUDED.working_days,
        working_hours = EXCLUDED.working_hours,
        is_24_7 = EXCLUDED.is_24_7,
        updated_at = now()
    """
    try:
        async with pool.acquire() as conn:
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
        logger.error(f"❌ Error inserting carwash: {e}")
        return False

async def get_all_autoservices() -> List[Dict[str, Any]]:
    """
    Retrieve all autoservices from the database.
    
    Returns:
        List[Dict[str, Any]]: List of autoservice records as dictionaries.
    """
    global pool
    if pool is None:
        await init_db()
    
    query = "SELECT * FROM autoservice"
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(query)
            return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"❌ Error fetching autoservices: {e}")
        return []

async def get_all_carwashes() -> List[Dict[str, Any]]:
    """
    Retrieve all carwashes from the database.
    
    Returns:
        List[Dict[str, Any]]: List of carwash records as dictionaries.
    """
    global pool
    if pool is None:
        await init_db()
    
    query = "SELECT * FROM carwash"
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(query)
            return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"❌ Error fetching carwashes: {e}")
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
        List[Dict[str, Any]]: List of nearby places sorted by distance, limited to 10 results.
        
    Raises:
        ValueError: If place_type is not "autoservice" or "carwash"
    """
    global pool
    if pool is None:
        await init_db()
        if pool is None:
            logger.error("❌ Database pool not initialized")
            return []
    
    # Validate place_type to prevent SQL injection
    if place_type not in ("autoservice", "carwash"):
        logger.error(f"❌ Invalid place_type: {place_type}")
        raise ValueError(f"Invalid place_type: {place_type}. Must be 'autoservice' or 'carwash'")
    
    # Validate coordinates
    if not (-90 <= lat <= 90):
        logger.error(f"❌ Invalid latitude: {lat}")
        raise ValueError(f"Invalid latitude: {lat}. Must be between -90 and 90")
    if not (-180 <= lon <= 180):
        logger.error(f"❌ Invalid longitude: {lon}")
        raise ValueError(f"Invalid longitude: {lon}. Must be between -180 and 180")
    
    # Haversine formula for distance calculation
    query = f"""
    SELECT *,
        (6371 * acos(cos(radians($1)) * cos(radians(lat)) * 
        cos(radians(lon) - radians($2)) + sin(radians($1)) * 
        sin(radians(lat)))) AS distance_km
    FROM {place_type}
    WHERE (6371 * acos(cos(radians($1)) * cos(radians(lat)) * 
        cos(radians(lon) - radians($2)) + sin(radians($1)) * 
        sin(radians(lat)))) < $3
    ORDER BY distance_km
    LIMIT 10
    """
    
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, lat, lon, radius_km)
            return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"❌ Error finding nearby places: {e}")
        return []

# ... (qolgan funksiyalar o'zgarmaydi)

async def search_places_by_service(service_name: str, place_type: str = "autoservice") -> List[Dict[str, Any]]:
    """
    Search places by service name.
    
    Args:
        service_name: Name of the service to search for
        place_type: Type of place ("autoservice" or "carwash")
        
    Returns:
        List[Dict[str, Any]]: List of places offering the specified service.
        
    Raises:
        ValueError: If place_type is not "autoservice" or "carwash"
    """
    # Validate place_type to prevent SQL injection
    if place_type not in ("autoservice", "carwash"):
        logger.error(f"❌ Invalid place_type: {place_type}")
        raise ValueError(f"Invalid place_type: {place_type}. Must be 'autoservice' or 'carwash'")
    
    query = f"SELECT * FROM {place_type} WHERE services @> $1::jsonb"
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, json.dumps([service_name]))
            return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"❌ Error searching by service: {e}")
        return []

# ================== BATCH OPERATIONLARI ==================

async def batch_insert_autoservices(services_data: List[Dict[str, Any]]) -> bool:
    """
    Insert multiple autoservices in a single transaction.
    
    Args:
        services_data: List of autoservice data dictionaries
        
    Returns:
        bool: True if all insertions were successful, False otherwise.
    """
    try:
        async with pool.acquire() as conn:
            async with conn.transaction():
                for data in services_data:
                    await insert_autoservice(data)
        return True
    except Exception as e:
        logger.error(f"❌ Batch insert error: {e}")
        return False

async def batch_insert_carwashes(carwashes_data: List[Dict[str, Any]]) -> bool:
    """
    Insert multiple carwashes in a single transaction.
    
    Args:
        carwashes_data: List of carwash data dictionaries
        
    Returns:
        bool: True if all insertions were successful, False otherwise.
    """
    try:
        async with pool.acquire() as conn:
            async with conn.transaction():
                for data in carwashes_data:
                    await insert_carwash(data)
        return True
    except Exception as e:
        logger.error(f"❌ Batch insert error: {e}")
        return False

# ================== TEST QISMI ==================

async def test_database() -> None:
    """
    Test database functionality with sample data.
    
    This function creates test autoservice entries and verifies
    database operations including insert, fetch, and search.
    """
    await init_db()
    
    # Test data
    test_autoservice = {
        "id": "test_1",
        "name": "Test Autoservice",
        "lat": 41.311081,
        "lon": 69.240562,
        "address": "Test address",
        "phone": "+998901234567",
        "services": ["Elektrik", "Motarius"],
        "working_days": [0, 1, 2, 3, 4],
        "working_hours": {"start": "09:00", "end": "18:00"},
        "is_24_7": False
    }
    
    # Insert test
    success = await insert_autoservice(test_autoservice)
    print(f"✅ Insert test: {'Successful' if success else 'Failed'}")
    
    # Fetch test
    services = await get_all_autoservices()
    print(f"✅ Fetch test: {len(services)} service(s) found")
    
    # Search test
    nearby = await get_nearby_places(41.311081, 69.240562, 5.0)
    print(f"✅ Search test: {len(nearby)} nearby place(s) found")
    
    await close_db()

if __name__ == "__main__":
    asyncio.run(test_database())
