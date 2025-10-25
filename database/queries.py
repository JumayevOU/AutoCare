"""
SQL query definitions.
"""

QUERIES = {
    "insert_autoservice": """
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
    """,
    
    "insert_carwash": """
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
    """,
    
    "nearby_places": """
        SELECT *,
            (6371 * acos(cos(radians($1)) * cos(radians(lat)) * 
            cos(radians(lon) - radians($2)) + sin(radians($1)) * 
            sin(radians(lat)))) AS distance_km
        FROM {table}
        WHERE (6371 * acos(cos(radians($1)) * cos(radians(lat)) * 
            cos(radians(lon) - radians($2)) + sin(radians($1)) * 
            sin(radians(lat)))) < $3
        ORDER BY distance_km
        LIMIT 10
    """
}