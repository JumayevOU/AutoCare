from aiogram import Router, types
from aiogram.filters import CommandStart
from keyboards.inline.menu import categoryMenu

router = Router()


@router.message(CommandStart())
async def bot_start(message: types.Message):
    await message.answer(
        f"Salom, {message.from_user.full_name}! 👋",reply_markup=categoryMenu)
