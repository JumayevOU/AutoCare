"""
Rate limiting middleware for aiogram 3.x bot.

Prevents users from flooding the bot with too many requests.
"""
import time
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
import logging

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseMiddleware):
    """
    Middleware to implement rate limiting for bot messages and callbacks.
    
    Attributes:
        rate_limit: Time in seconds between allowed requests per user
        user_last_request: Dictionary storing last request time for each user
    """
    
    def __init__(self, rate_limit: float = 1.0):
        """
        Initialize rate limit middleware.
        
        Args:
            rate_limit: Minimum time in seconds between requests (default: 1.0)
        """
        super().__init__()
        self.rate_limit = rate_limit
        self.user_last_request: Dict[int, float] = {}
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        """
        Check rate limit before processing the request.
        
        Args:
            handler: The handler function to call
            event: The Telegram event (Message or CallbackQuery)
            data: Additional data passed to the handler
            
        Returns:
            The result of the handler, or None if rate limited
        """
        user_id = None
        
        # Extract user_id from different event types
        if isinstance(event, Message):
            user_id = event.from_user.id if event.from_user else None
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id if event.from_user else None
        
        # If we can't determine user_id, allow the request
        if user_id is None:
            return await handler(event, data)
        
        current_time = time.time()
        last_request_time = self.user_last_request.get(user_id, 0)
        time_passed = current_time - last_request_time
        
        # Check if enough time has passed since last request
        if time_passed < self.rate_limit:
            # Rate limit exceeded
            remaining_time = self.rate_limit - time_passed
            logger.warning(
                f"Rate limit exceeded for user {user_id}. "
                f"Need to wait {remaining_time:.1f}s more."
            )
            
            # Respond to user about rate limiting
            if isinstance(event, Message):
                await event.answer(
                    "⏱ Iltimos, bir oz kuting. Juda tez so'rov yuborayapsiz.\n"
                    "⏱ Please wait a moment. You're sending requests too quickly."
                )
            elif isinstance(event, CallbackQuery):
                await event.answer(
                    "⏱ Iltimos, bir oz kuting / Please wait a moment",
                    show_alert=True
                )
            
            return None
        
        # Update last request time and process the request
        self.user_last_request[user_id] = current_time
        return await handler(event, data)
