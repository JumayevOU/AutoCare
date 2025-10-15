import logging
from typing import Optional

from aiogram import Dispatcher
from aiogram.types import Update
import aiogram.exceptions as ai_exc
import aiogram.methods as ai_methods

try:
    from loader import dp
except Exception:
    dp = None  

logger = logging.getLogger(__name__)

MessageNotModified = getattr(ai_methods, "MessageNotModified", getattr(ai_exc, "MessageNotModified", Exception))
MessageToDeleteNotFound = getattr(ai_methods, "MessageToDeleteNotFound", getattr(ai_exc, "MessageToDeleteNotFound", Exception))
MessageCantBeDeleted = getattr(ai_methods, "MessageCantBeDeleted", getattr(ai_exc, "MessageCantBeDeleted", Exception))
MessageTextIsEmpty = getattr(ai_methods, "MessageTextIsEmpty", getattr(ai_exc, "MessageTextIsEmpty", Exception))

Unauthorized = getattr(ai_exc, "Unauthorized", Exception)
InvalidQueryID = getattr(ai_exc, "InvalidQueryID", Exception)
TelegramAPIError = getattr(ai_exc, "TelegramAPIError", Exception)
RetryAfter = getattr(ai_exc, "RetryAfter", Exception)
CantParseEntities = getattr(ai_exc, "CantParseEntities", Exception)


async def errors_handler(update: Optional[Update], exception: Exception) -> bool:
    """
    Global xatolik tutuvchi handler (aiogram 3.22.0 mos).
    Aiogram uchun handler signature: (update, exception). Update None bo'lishi mumkin.
    Handler True qaytarsa, xatolik 'handled' deb hisoblanadi.
    """

    if isinstance(exception, MessageNotModified):
        logger.debug("Message is not modified: %s", exception, exc_info=True)
        return True

    if isinstance(exception, MessageCantBeDeleted):
        logger.debug("Message can't be deleted: %s", exception, exc_info=True)
        return True

    if isinstance(exception, MessageToDeleteNotFound):
        logger.debug("Message to delete not found: %s", exception, exc_info=True)
        return True

    if isinstance(exception, MessageTextIsEmpty):
        logger.debug("Message text is empty: %s", exception, exc_info=True)
        return True

    if isinstance(exception, Unauthorized):
        logger.exception("Unauthorized: %s", exception)
        return True

    if isinstance(exception, InvalidQueryID):
        logger.exception("InvalidQueryID: %s\nUpdate: %s", exception, update)
        return True

    if isinstance(exception, TelegramAPIError):
        logger.exception("TelegramAPIError: %s\nUpdate: %s", exception, update)
        return True

    if isinstance(exception, RetryAfter):
        logger.exception("RetryAfter: %s\nUpdate: %s", exception, update)
        return True

    if isinstance(exception, CantParseEntities):
        logger.exception("CantParseEntities: %s\nUpdate: %s", exception, update)
        return True

    logger.exception("Unhandled exception\nUpdate: %s\nException: %s", update, exception)
    return True


def register_error_handlers(dispatcher: Dispatcher) -> None:
    """
    Dispatcher ga error handler ni ro'yxatdan o'tkazadi.
    Aiogram 3.x: dispatcher.errors.register(handler)
    """
    dispatcher.errors.register(errors_handler)


