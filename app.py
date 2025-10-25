# app.py
"""
Main application file for AutoCare Telegram Bot.

This bot helps users find nearby autoservices and carwashes
in Uzbekistan using location-based search.
"""
import asyncio
import logging
import os
from aiogram import Bot, Dispatcher

from handlers import setup_routers
from database import init_db, close_db
from middlewares.rate_limit import RateLimitMiddleware


def setup_logging() -> None:
    """Configure logging with proper format and level."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    # Reduce noise from some libraries
    logging.getLogger("aiogram.event").setLevel(logging.WARNING)


async def main() -> None:
    """
    Main entry point for the bot application.
    
    Initializes database, sets up bot and dispatcher,
    registers handlers and middlewares, then starts polling.
    """
    setup_logging()
    
    # Initialize database
    try:
        await init_db()
        logging.info("✅ Database initialized successfully")
    except Exception as e:
        logging.error(f"❌ Database initialization error: {e}")
        return
    
    # Get bot token from environment
    api_token = os.getenv("BOT_TOKEN")
    if not api_token:
        logging.error("❌ BOT_TOKEN environment variable not found")
        return
    
    bot = Bot(token=api_token)
    dp = Dispatcher()
    
    # Register rate limiting middleware (1 request per second per user)
    dp.message.middleware(RateLimitMiddleware(rate_limit=1.0))
    dp.callback_query.middleware(RateLimitMiddleware(rate_limit=0.5))
    
    # Setup routers
    setup_routers(dp)
    
    try:
        logging.info("🤖 Bot starting...")
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"❌ Bot startup error: {e}")
    finally:
        await close_db()
        await bot.session.close()
        logging.info("👋 Bot stopped")


if __name__ == "__main__":
    asyncio.run(main())
