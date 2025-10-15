# app.py
import asyncio
import logging
import os
from aiogram import Bot, Dispatcher

from handlers import setup_routers
from database import init_db, close_db

async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    
    # Database ni ishga tushirish
    try:
        await init_db()
        logging.info("✅ Database muvaffaqiyatli ishga tushirildi")
    except Exception as e:
        logging.error(f"❌ Database ni ishga tushirishda xatolik: {e}")
        return
    
    # Environment variabledan token o'qish
    API_TOKEN = os.getenv("BOT_TOKEN")
    if not API_TOKEN:
        logging.error("❌ BOT_TOKEN environment variable topilmadi")
        return
    
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()
    
    # Routerlarni sozlash - TO'G'RI USUL
    setup_routers(dp)  # dp ni argument sifatida beramiz
    
    try:
        logging.info("🤖 Bot ishga tushmoqda...")
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"❌ Bot ishga tushishda xatolik: {e}")
    finally:
        await close_db()
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
