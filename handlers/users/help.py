import logging
from typing import List, Optional

from aiogram import Router, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
try:
    from loader import dp
except Exception:
    dp = None

logger = logging.getLogger(__name__)

router = Router(name="users_help")


@router.message(Command(commands=["help"]))  
async def bot_help(message: Message) -> None:
    lines: List[str] = [
        "Buyruqlar:",
        "/start - Botni ishga tushirish",
        "/help - Yordam",
    ]
    await message.answer("\n".join(lines))


def register_help_router(dispatcher: Dispatcher) -> None:
    dispatcher.include_router(router)


if dp is not None:
    try:
        dp.include_router(router)
        logger.info("Help router auto-registered on dp.")
    except Exception:
        logger.exception("Couldn't auto-register help router. Call register_help_router(dp) manually.")
