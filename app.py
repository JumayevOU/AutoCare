import asyncio
from loader import dp, bot
from handlers import setup_routers

async def main():
    await dp.start_polling(bot)

    routers = setup_routers()
    for router in routers:
        dp.include_router(router)

    try:
        await dp.start_polling(bot)
    finally:
        await close_db()
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())
