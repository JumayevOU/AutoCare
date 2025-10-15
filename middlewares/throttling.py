import asyncio
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: float = 1.0, key_prefix: str = "antiflood_"):
        super().__init__()
        self.rate_limit = rate_limit
        self.prefix = key_prefix
        self.user_timestamps: dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        user_id = event.from_user.id if event.from_user else None
        if user_id is None:
            return await handler(event, data)

        key = f"{self.prefix}{user_id}"

        now = asyncio.get_event_loop().time()
        last_time = self.user_timestamps.get(user_id, 0)
        delta = now - last_time

        if delta < self.rate_limit:
            await self.message_throttled(event, delta)
            raise Exception(f"Throttled: {key}")

        self.user_timestamps[user_id] = now
        return await handler(event, data)

    async def message_throttled(self, message: Message, delta: float):
        await message.reply("❗ Juda tez yuboryapsiz, biroz kuting...")
