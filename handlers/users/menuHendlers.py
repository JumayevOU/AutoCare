# handlers/users/menuHendlers.py
from typing import Optional
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ParseMode
from keyboards.inline.menu import xizmatlar, categoryMenu
from keyboards.default.location_button import keyboard

# locations_hendler dan user_place_type ni import qilamiz
from handlers.users.locations_hendler import user_place_type

try:
    from loader import dp  
except Exception:
    dp = None

router = Router(name="services")

@router.callback_query(F.data == "avtoservis")
async def on_avtoservis(call: CallbackQuery) -> None:
    await call.answer()
    # user_place_type ga qo'shamiz
    user_place_type[call.from_user.id] = "autoservice"
    print(f"DEBUG: avtoservis tanlandi - user_id: {call.from_user.id}")
    
    if call.message:
        try:
            await call.message.delete()
        except Exception:
            pass
        await call.message.answer("Xizmat turini tanlang ⤵️", reply_markup=xizmatlar)
    else:
        return

@router.callback_query(F.data == "moyka")
async def on_moyka(call: CallbackQuery) -> None:
    await call.answer()
    # user_place_type ga qo'shamiz
    user_place_type[call.from_user.id] = "carwash"
    print(f"DEBUG: moyka tanlandi - user_id: {call.from_user.id}")
    
    text = "<b>📍 Joylashuvingizni yuboring</b>, biz sizga eng yaqin <b>Avtomoyka</b>larni ko'rsatamiz 🤩"
    if call.message:
        await call.message.answer(text, parse_mode=ParseMode.HTML, reply_markup=keyboard)

# HAR BIR XIZMAT TURI UCHUN user_place_type GA QO'SHAMIZ
@router.callback_query(F.data == "elektrik")
async def on_elektrik(call: CallbackQuery) -> None:
    await call.answer()
    user_place_type[call.from_user.id] = "autoservice"
    print(f"DEBUG: elektrik tanlandi - user_id: {call.from_user.id}")
    
    text = "<b>📍 Joylashuvingizni yuboring</b>, biz sizga eng yaqin <b>Elektrik</b>larni ko'rsatamiz 🤩"
    if call.message:
        await call.message.answer(text, parse_mode=ParseMode.HTML, reply_markup=keyboard)

@router.callback_query(F.data == "kuzov")
async def on_kuzov(call: CallbackQuery) -> None:
    await call.answer()
    user_place_type[call.from_user.id] = "autoservice"
    print(f"DEBUG: kuzov tanlandi - user_id: {call.from_user.id}")
    
    text = "<b>📍 Joylashuvingizni yuboring</b>, biz sizga eng yaqin <b>Avtoservice</b>larni ko'rsatamiz 🤩"
    if call.message:
        await call.message.answer(text, parse_mode=ParseMode.HTML, reply_markup=keyboard)

@router.callback_query(F.data == "motor")
async def on_motor(call: CallbackQuery) -> None:
    await call.answer()
    user_place_type[call.from_user.id] = "autoservice"
    print(f"DEBUG: motor tanlandi - user_id: {call.from_user.id}")
    
    text = "<b>📍 Joylashuvingizni yuboring</b>, biz sizga eng yaqin <b>Avtoservice</b>larni ko'rsatamiz 🤩"
    if call.message:
        await call.message.answer(text, parse_mode=ParseMode.HTML, reply_markup=keyboard)

@router.callback_query(F.data == "vulkanizatsiya")
async def on_vulkanizatsiya(call: CallbackQuery) -> None:
    await call.answer()
    user_place_type[call.from_user.id] = "autoservice"
    print(f"DEBUG: vulkanizatsiya tanlandi - user_id: {call.from_user.id}")
    
    text = "<b>📍 Joylashuvingizni yuboring</b>, biz sizga eng yaqin <b>Vulkanizatsiya</b>larni ko'rsatamiz 🤩"
    if call.message:
        await call.message.answer(text, parse_mode=ParseMode.HTML, reply_markup=keyboard)

@router.callback_query(F.data == "balon")
async def on_balon(call: CallbackQuery) -> None:
    await call.answer()
    user_place_type[call.from_user.id] = "autoservice"
    print(f"DEBUG: balon tanlandi - user_id: {call.from_user.id}")
    
    text = "<b>📍 Joylashuvingizni yuboring</b>, biz sizga eng yaqin <b>Avtoservice</b>larni ko'rsatamiz 🤩"
    if call.message:
        await call.message.answer(text, parse_mode=ParseMode.HTML, reply_markup=keyboard)

@router.callback_query(F.data == "tanirovka")
async def on_tanirovka(call: CallbackQuery) -> None:
    await call.answer()
    user_place_type[call.from_user.id] = "autoservice"
    print(f"DEBUG: tanirovka tanlandi - user_id: {call.from_user.id}")
    
    text = "<b>📍 Joylashuvingizni yuboring</b>, biz sizga eng yaqin <b>Avtoservice</b>larni ko'rsatamiz 🤩"
    if call.message:
        await call.message.answer(text, parse_mode=ParseMode.HTML, reply_markup=keyboard)

@router.callback_query(F.data == "shumka")
async def on_shumka(call: CallbackQuery) -> None:
    await call.answer()
    user_place_type[call.from_user.id] = "autoservice"
    print(f"DEBUG: shumka tanlandi - user_id: {call.from_user.id}")
    
    text = "<b>📍 Joylashuvingizni yuboring</b>, biz sizga eng yaqin <b>Avtoservice</b>larni ko'rsatamiz 🤩"
    if call.message:
        await call.message.answer(text, parse_mode=ParseMode.HTML, reply_markup=keyboard)

@router.callback_query(F.data == "universal")
async def on_universal(call: CallbackQuery) -> None:
    await call.answer()
    user_place_type[call.from_user.id] = "autoservice"
    print(f"DEBUG: universal tanlandi - user_id: {call.from_user.id}")
    
    text = "<b>📍 Joylashuvingizni yuboring</b>, biz sizga eng yaqin <b>Avtoservice</b>larni ko'rsatamiz 🤩"
    if call.message:
        await call.message.answer(text, parse_mode=ParseMode.HTML, reply_markup=keyboard)




@router.callback_query(F.data == "security")
async def on_security(call: CallbackQuery) -> None:
    await call.answer()
    text = (
        "🛡️ <b>Bloklashga qarshi tizim</b>\n\n"
        "Hozirda bu bo‘lim ishlamayapti — ustida ish olib borilayapti. "
        "Tez orada qayta ishga tushiriladi. \n\n"
        "Asosiy menyuga qaytamiz."
    )
    if call.message:
        await call.message.answer(text, parse_mode=ParseMode.HTML, reply_markup=categoryMenu)


@router.callback_query(F.data == "fuel")
async def on_fuel(call: CallbackQuery) -> None:
    await call.answer()
    text = (
        "⛽ <b>Yoqilg‘i yetqazib berish</b>\n\n"
        "Hozirda bu bo‘lim ishlamayapti — ustida ish olib borilayapti. "
        "Tez orada xizmat joriy etiladi. \n\n"
        "Asosiy menyuga qaytamiz."
    )
    if call.message:
        await call.message.answer(text, parse_mode=ParseMode.HTML, reply_markup=categoryMenu)


@router.message(F.text == "🔙Ortga")
async def on_go_back_services(message: Message) -> None:
    await message.answer(
        "🔙 Xizmatlar bo‘limiga qaytdingiz. Quyidagilardan birini tanlang:",
        reply_markup=xizmatlar
    )


@router.message(F.text == "📚Menyu")
async def on_go_back_menu(message: Message) -> None:
    await message.answer(
        "📚 Asosiy menyuga qaytdingiz. Quyidagilardan birini tanlang:",
        reply_markup=categoryMenu
    )



