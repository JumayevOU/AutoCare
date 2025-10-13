from aiogram.types import Message, CallbackQuery
from keyboards.inline.menu import xizmatlar,categoryMenu
from keyboards.default.location_button import keyboard
from loader import dp




@dp.callback_query_handler(text='avtoservis')
async def select_category(call: CallbackQuery):
    await call.answer()
    await call.message.delete()
    await call.message.answer("Xizmat turini tanlang ⤵️", reply_markup=xizmatlar)


from aiogram.types import CallbackQuery

@dp.callback_query_handler(text='elektrik')
async def select_category(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "<b>📍 Joylashuvingizni jo‘nating</b>, biz sizga eng yaqin <b>Elektrik</b>larni ko‘rsatamiz 🤩",
        parse_mode="HTML",
        reply_markup=keyboard
    )

@dp.message_handler(text="🔙Ortga")
async def go_back_services(message: Message):
    await message.answer(
        "🔙 Xizmatlar bo‘limiga qaytdingiz. Quyidagilardan birini tanlang:",
        reply_markup=xizmatlar
    )


@dp.message_handler(text="📚Menyu")
async def go_back_menu(message: Message):
    await message.answer(
        "📚 Asosiy menyuga qaytdingiz. Quyidagilardan birini tanlang:",
        reply_markup=categoryMenu
    )
   
@dp.callback_query_handler(text='kuzov')
async def select_category(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "<b>📍 Joylashuvingizni jo‘nating</b>, biz sizga eng yaqin <b>Avtoservice</b>larni ko‘rsatamiz 🤩",
        parse_mode="HTML",
        reply_markup=keyboard
    )
    
@dp.callback_query_handler(text='motor')
async def select_category(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "<b>📍 Joylashuvingizni jo‘nating</b>, biz sizga eng yaqin <b>Avtoservice</b>larni ko‘rsatamiz 🤩",
        parse_mode="HTML",
        reply_markup=keyboard
    )
    
@dp.callback_query_handler(text='vulkanizatsiya')
async def select_category(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "<b>📍 Joylashuvingizni jo‘nating</b>, biz sizga eng yaqin <b>Vulkanizatsiya</b>larni ko‘rsatamiz 🤩",
        parse_mode="HTML",
        reply_markup=keyboard
    )        


@dp.callback_query_handler(text='balon')
async def select_category(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "<b>📍 Joylashuvingizni jo‘nating</b>, biz sizga eng yaqin <b>Avtoservice</b>larni ko‘rsatamiz 🤩",
        parse_mode="HTML",
        reply_markup=keyboard
    )
    
    
@dp.callback_query_handler(text='tanirovka')
async def select_category(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "<b>📍 Joylashuvingizni jo‘nating</b>, biz sizga eng yaqin <b>Avtoservice</b>larni ko‘rsatamiz 🤩",
        parse_mode="HTML",
        reply_markup=keyboard
    )
    

@dp.callback_query_handler(text='shumka')
async def select_category(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "<b>📍 Joylashuvingizni jo‘nating</b>, biz sizga eng yaqin <b>Avtoservice</b>larni ko‘rsatamiz 🤩",
        parse_mode="HTML",
        reply_markup=keyboard
    )
   
@dp.callback_query_handler(text='universal')
async def select_category(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(
        "<b>📍 Joylashuvingizni jo‘nating</b>, biz sizga eng yaqin <b>Avtoservice</b>larni ko‘rsatamiz 🤩",
        parse_mode="HTML",
        reply_markup=keyboard
    )
    
                
@dp.callback_query_handler(text="security")
async def handle_security(call: CallbackQuery):
    await call.answer()
    text = (
        "🛡️ <b>Bloklashga qarshi tizim</b>\n\n"
        "Hozirda bu bo‘lim ishlamayapti — ustida ish olib borilayapti. "
        "Tez orada qayta ishga tushiriladi. \n\n"
        "Asosiy menyuga qaytamiz."
    )
    await call.message.answer(text, parse_mode="HTML", reply_markup=categoryMenu)


@dp.callback_query_handler(text="fuel")
async def handle_fuel(call: CallbackQuery):
    await call.answer()
    text = (
        "⛽ <b>Yoqilg‘i yetqazib berish</b>\n\n"
        "Hozirda bu bo‘lim ishlamayapti — ustida ish olib borilayapti. "
        "Tez orada xizmat joriy etiladi. \n\n"
        "Asosiy menyuga qaytamiz."
    )
    await call.message.answer(text, parse_mode="HTML", reply_markup=categoryMenu)