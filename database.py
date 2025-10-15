# database.py
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
    """Database va connection pool ni ishga tushiradi"""
    global pool
    db_url = database_url or DATABASE_URL
    
    if not db_url:
        logger.error("❌ DATABASE_URL muhit o'zgaruvchisi topilmadi")
        return
    
    try:
        pool = await asyncpg.create_pool(
            db_url,
            min_size=1,
            max_size=10,
            command_timeout=60
        )
        
        async with pool.acquire() as conn:
            await conn.execute(CREATE_TABLES_SQL)
            logger.info("✅ Database jadvallari yaratildi/tekshirildi")
            
    except Exception as e:
        logger.error(f"❌ Database ni ishga tushirishda xatolik: {e}")
        pool = None
        raise

async def close_db() -> None:
    """Connection pool ni yopadi"""
    global pool
    if pool:
        await pool.close()
        pool = None

async def get_connection():
    """Connection olish"""
    global pool
    if pool is None:
        await init_db()
    return await pool.acquire()

async def release_connection(conn):
    """Connection ni qaytarish"""
    await pool.release(conn)

# ================== CRUD OPERATIONLARI ==================

async def insert_autoservice(data: Dict[str, Any]) -> bool:
    """Avtoservis qo'shish"""
    global pool
    if pool is None:
        await init_db()
    
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
        logger.error(f"❌ Avtoservis qo'shishda xatolik: {e}")
        return False

async def insert_carwash(data: Dict[str, Any]) -> bool:
    """Avtomoyka qo'shish"""
    global pool
    if pool is None:
        await init_db()
    
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
        logger.error(f"❌ Avtomoyka qo'shishda xatolik: {e}")
        return False

async def get_all_autoservices() -> List[Dict[str, Any]]:
    """Barcha avtoservislarni olish"""
    global pool
    if pool is None:
        await init_db()
    
    query = "SELECT * FROM autoservice"
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(query)
            return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"❌ Avtoservislarni olishda xatolik: {e}")
        return []

async def get_all_carwashes() -> List[Dict[str, Any]]:
    """Barcha avtomoykalarni olish"""
    global pool
    if pool is None:
        await init_db()
    
    query = "SELECT * FROM carwash"
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(query)
            return [dict(row) for row in rows]
    except Exception as e:
        logger.error(f"❌ Avtomoykalarni olishda xatolik: {e}")
        return []

async def get_nearby_places(lat: float, lon: float, radius_km: float = 50.0, place_type: str = "autoservice") -> List[Dict[str, Any]]:
    """
    Berilgan koordinatalarga yaqin joylarni topish
    """
    global pool
    if pool is None:
        await init_db()
        if pool is None:
            logger.error("❌ Database pool hali ishga tushmadi")
            return []
    
    # Haversine formulasi bilan masofa hisoblash
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
        logger.error(f"❌ Yaqin joylarni topishda xatolik: {e}")
        return []

# ... (qolgan funksiyalar o'zgarmaydi)

async def search_places_by_service(service_name: str, place_type: str = "autoservice") -> List[Dict[str, Any]]:
    """
    Xizmat nomi bo'yicha qidirish
    """
    query = f"SELECT * FROM {place_type} WHERE services @> $1::jsonb"
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, json.dumps([service_name]))
            return [dict(row) for row in rows]
    except Exception as e:
        print(f"❌ Xizmat bo'yicha qidirishda xatolik: {e}")
        return []

# ================== BATCH OPERATIONLARI ==================

async def batch_insert_autoservices(services_data: List[Dict[str, Any]]) -> bool:
    """Bir nechta avtoservislarni bir vaqtda qo'shish"""
    try:
        async with pool.acquire() as conn:
            async with conn.transaction():
                for data in services_data:
                    await insert_autoservice(data)
        return True
    except Exception as e:
        print(f"❌ Batch insert xatolik: {e}")
        return False

async def batch_insert_carwashes(carwashes_data: List[Dict[str, Any]]) -> bool:
    """Bir nechta avtomoykalarni bir vaqtda qo'shish"""
    try:
        async with pool.acquire() as conn:
            async with conn.transaction():
                for data in carwashes_data:
                    await insert_carwash(data)
        return True
    except Exception as e:
        print(f"❌ Batch insert xatolik: {e}")
        return False

# ================== TEST QISMI ==================

async def test_database():
    """Database funksionalligini test qilish"""
    await init_db()
    
    # Test ma'lumotlari
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
    
    # Qo'shish testi
    success = await insert_autoservice(test_autoservice)
    print(f"✅ Qo'shish testi: {'Muvaffaqiyatli' if success else 'Muvaffaqiyatsiz'}")
    
    # O'qish testi
    services = await get_all_autoservices()
    print(f"✅ O'qish testi: {len(services)} ta servis topildi")
    
    # Qidiruv testi
    nearby = await get_nearby_places(41.311081, 69.240562, 5.0)
    print(f"✅ Qidiruv testi: {len(nearby)} ta yaqin joy topildi")
    
    await close_db()

if __name__ == "__main__":
    asyncio.run(test_database())
