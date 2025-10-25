"""
Database table definitions and schemas.
"""

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

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_autoservice_coords ON autoservice(lat, lon);
CREATE INDEX IF NOT EXISTS idx_carwash_coords ON carwash(lat, lon);
CREATE INDEX IF NOT EXISTS idx_autoservice_services ON autoservice USING GIN(services);
CREATE INDEX IF NOT EXISTS idx_carwash_services ON carwash USING GIN(services);
"""

# Table field definitions for validation
REQUIRED_FIELDS = {
    'autoservice': ['id', 'name', 'lat', 'lon'],
    'carwash': ['id', 'name', 'lat', 'lon']
}

OPTIONAL_FIELDS = {
    'autoservice': ['address', 'phone', 'services', 'working_days', 'working_hours', 'is_24_7'],
    'carwash': ['address', 'phone', 'services', 'working_days', 'working_hours', 'is_24_7']
}