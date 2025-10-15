import os
import asyncio
import asyncpg
import json
from typing import Dict, Any, List, Optional

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://username:password@host:port/dbname")

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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);
"""

async def init_db(database_url: Optional[str] = None) -> None:
    """Jadvallarni yaratadi (agar mavjud bo'lmasa)."""
    db_url = database_url or DATABASE_URL
    conn = await asyncpg.connect(db_url)
    try:
        await conn.execute(CREATE_TABLES_SQL)
        print("✅ Jadval(lar) yaratildi yoki mavjudligi tekshirildi.")
    finally:
        await conn.close()

async def insert_generic(table: str, data: Dict[str, Any]) -> None:
    """
    Umumiy qo'shish funktsiyasi.
    data quyidagi kalitlarni olishi kerak: id, name, lat, lon, address, phone,
    services (list), working_days (list of ints), working_hours (dict), is_24_7 (bool)
    """
    db_url = DATABASE_URL
    query = f"""
    INSERT INTO {table} (
        id, name, lat, lon, address, phone, services, working_days, working_hours, is_24_7
    ) VALUES (
        $1, $2, $3, $4, $5, $6, $7::jsonb, $8::int[], $9::jsonb, $10
    )
    ON CONFLICT (id) DO NOTHING;
    """
    conn = await asyncpg.connect(db_url)
    try:
        services_json = json.dumps(data.get("services", []))
        working_hours_json = json.dumps(data.get("working_hours", {}))
        working_days_list = data.get("working_days", [])
        await conn.execute(
            query,
            data["id"],
            data["name"],
            float(data["lat"]),
            float(data["lon"]),
            data.get("address"),
            data.get("phone"),
            services_json,
            working_days_list,
            working_hours_json,
            bool(data.get("is_24_7", False)),
        )
        print(f"✅ `{table}` ga `{data['id']}` qo'shildi (yoki allaqachon mavjud bo'lsa e'tiborsiz qoldirildi).")
    finally:
        await conn.close()

async def insert_autoservice(data: Dict[str, Any]) -> None:
    await insert_generic("autoservice", data)

async def insert_carwash(data: Dict[str, Any]) -> None:
    await insert_generic("carwash", data)


if __name__ == "__main__":
    asyncio.run(init_db())

