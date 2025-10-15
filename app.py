import asyncio
from aiogram import Bot, Dispatcher
from database import init_db, close_db

async def main():
    await init_db()
    
    bot = Bot(token=API_TOKEN)
    dp = Dispatcher()
    
    
    try:
        await dp.start_polling(bot)
    finally:
        await close_db()

if __name__ == "__main__":
    asyncio.run(main())
