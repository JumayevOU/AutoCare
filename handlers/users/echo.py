from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

router = Router()

@router.message(F.text)
async def bot_echo(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer(message.text)
