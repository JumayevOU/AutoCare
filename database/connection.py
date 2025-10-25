import os
import asyncpg
import logging
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
print(f"Loaded DATABASE_URL: {DATABASE_URL}")

# Global connection pool
pool: Optional[asyncpg.Pool] = None

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
    
    logger.info(f"ℹ️ Using DATABASE_URL: {db_url.split('@')[-1]}")
    
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
        
        from .models import CREATE_TABLES_SQL
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

def get_pool() -> Optional[asyncpg.Pool]:
    """Get the current connection pool."""
    return pool