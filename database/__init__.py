"""
Database module for AutoCare bot.
Provides PostgreSQL database operations with connection pooling.
"""
from .connection import init_db, close_db, get_connection, release_connection
from .crud import (
    insert_autoservice, insert_carwash,
    get_all_autoservices, get_all_carwashes,
    get_nearby_places, search_places_by_service,
    batch_insert_autoservices, batch_insert_carwashes
)
from .models import CREATE_TABLES_SQL

__all__ = [
    "init_db", "close_db", "get_connection", "release_connection",
    "insert_autoservice", "insert_carwash", 
    "get_all_autoservices", "get_all_carwashes",
    "get_nearby_places", "search_places_by_service",
    "batch_insert_autoservices", "batch_insert_carwashes",
    "CREATE_TABLES_SQL"
]