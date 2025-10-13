from aiogram import F, Router
from aiogram.types import Message, CallbackQuery
from keyboards.inline.menu import xizmatlar, categoryMenu
from keyboards.default.location_button import keyboard
from loader import dp

router = Router()


@router.callback_query(F.data == 'avtoservis')
async def select_category_avtoservice(call: CallbackQuery):
    await call.answer()
    try:
        await call.message.delete()
    except Exception:
        pass
    await call.message.answer("Xizmat turini tanlang ⤵️", reply_markup=xizmatlar)


@router.callback_query(F.data == 'elektrik')
async def select_category_elektrik(call: CallbackQuery):
    await call.answer()
    await call.message.answer(
        "<b>📍 Joylashuvingizni jo‘nating</b>, biz sizga eng yaqin <b>Elektrik</b>larni ko‘rsatamiz 🤩",
        parse_mode="HTML",
        reply_markup=keyboard
    )


@router.message(F.text == "🔙Ortga")
async def go_back_services(message: Message):
    await message.answer(
        "🔙 Xizmatlar bo‘limiga qaytdingiz. Quyidagilardan birini tanlang:",
        reply_markup=xizmatlar
    )


@router.message(F.text == "📚Menyu")
async def go_back_menu(message: Message):
    await message.answer(
        "📚 Asosiy menyuga qaytdingiz. Quyidagilardan birini tanlang:",
        reply_markup=categoryMenu
    )


@router.callback_query(F.data == 'kuzov')
async def select_category_kuzov(call: CallbackQuery):
    await call.answer()
    await call.message.answer(
        "<b>📍 Joylashuvingizni jo‘nating</b>, biz sizga eng yaqin <b>Avtoservice</b>larni ko‘rsatamiz 🤩",
        parse_mode="HTML",
        reply_markup=keyboard
    )


@router.callback_query(F.data == 'motor')
async def select_category_motor(call: CallbackQuery):
    await call.answer()
    await call.message.answer(
        "<b>📍 Joylashuvingizni jo‘nating</b>, biz sizga eng yaqin <b>Avtoservice</b>larni ko‘rsatamiz 🤩",
        parse_mode="HTML",
        reply_markup=keyboard
    )


@router.callback_query(F.data == 'vulkanizatsiya')
async def select_category_vulkanizatsiya(call: CallbackQuery):
    await call.answer()
    await call.message.answer(
        "<b>📍 Joylashuvingizni jo‘nating</b>, biz sizga eng yaqin <b>Vulkanizatsiya</b>larni ko‘rsatamiz 🤩",
        parse_mode="HTML",
        reply_markup=keyboard
    )


@router.callback_query(F.data == 'balon')
async def select_category_balon(call: CallbackQuery):
    await call.answer()
    await call.message.answer(
        "<b>📍 Joylashuvingizni jo‘nating</b>, biz sizga eng yaqin <b>Avtoservice</b>larni ko‘rsatamiz 🤩",
        parse_mode="HTML",
        reply_markup=keyboard
    )


@router.callback_query(F.data == 'tanirovka')
async def select_category_tanirovka(call: CallbackQuery):
    await call.answer()
    await call.message.answer(
        "<b>📍 Joylashuvingizni jo‘nating</b>, biz sizga eng yaqin <b>Avtoservice</b>larni ko‘rsatamiz 🤩",
        parse_mode="HTML",
        reply_markup=keyboard
    )


@router.callback_query(F.data == 'shumka')
async def select_category_shumka(call: CallbackQuery):
    await call.answer()
    await call.message.answer(
        "<b>📍 Joylashuvingizni jo‘nating</b>, biz sizga eng yaqin <b>Avtoservice</b>larni ko‘rsatamiz 🤩",
        parse_mode="HTML",
        reply_markup=keyboard
    )


@router.callback_query(F.data == 'universal')
async def select_category_universal(call: CallbackQuery):
    await call.answer()
    await call.message.answer(
        "<b>📍 Joylashuvingizni jo‘nating</b>, biz sizga eng yaqin <b>Avtoservice</b>larni ko‘rsatamiz 🤩",
        parse_mode="HTML",
        reply_markup=keyboard
    )


@router.callback_query(F.data == "security")
async def handle_security(call: CallbackQuery):
    await call.answer()
    text = (
        "🛡️ <b>Bloklashga qarshi tizim</b>\n\n"
        "Hozirda bu bo‘lim ishlamayapti — ustida ish olib borilayapti. "
        "Tez orada qayta ishga tushiriladi. \n\n"
        "Asosiy menyuga qaytamiz."
    )
    await call.message.answer(text, parse_mode="HTML", reply_markup=categoryMenu)


@router.callback_query(F.data == "fuel")
async def handle_fuel(call: CallbackQuery):
    await call.answer()
    text = (
        "⛽ <b>Yoqilg‘i yetqazib berish</b>\n\n"
        "Hozirda bu bo‘lim ishlamayapti — ustida ish olib borilayapti. "
        "Tez orada xizmat joriy etiladi. \n\n"
        "Asosiy menyuga qaytamiz."
    )
    await call.message.answer(text, parse_mode="HTML", reply_markup=categoryMenu)


dp.include_router(router)
