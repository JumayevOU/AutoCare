# handlers/admin_panel.py
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import insert_autoservice, insert_carwash, get_all_autoservices, get_all_carwashes, delete_autoservice, delete_carwash

router = Router()

# Admin ID laringizni shu yerga yozing
ADMIN_IDS = [2001717965]  # O'z ID laringizni qo'shing

class AddPlace(StatesGroup):
    choosing_type = State()
    entering_name = State()
    entering_location = State()
    entering_address = State()
    entering_phone = State()
    entering_services = State()
    entering_hours = State()
    confirmation = State()

def admin_required(func):
    """Admin tekshiruvi dekoratori"""
    async def wrapper(message: Message, *args, **kwargs):
        if message.from_user.id not in ADMIN_IDS:
            await message.answer("❌ Siz admin emassiz!")
            return
        return await func(message, *args, **kwargs)
    return wrapper

# ================== ADMIN PANEL MENYU ==================

@router.message(Command("admin"))
@admin_required
async def admin_panel(message: Message):
    """Admin panel asosiy menyusi"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🛠 Avtoservis qo'shish"), KeyboardButton(text="🚗 Avtomoyka qo'shish")],
            [KeyboardButton(text="📋 Avtoservislar ro'yxati"), KeyboardButton(text="📋 Avtomoykalar ro'yxati")],
            [KeyboardButton(text="🗑 Avtoservis o'chirish"), KeyboardButton(text="🗑 Avtomoyka o'chirish")],
            [KeyboardButton(text="📊 Statistika"), KeyboardButton(text="🚪 Admin paneldan chiqish")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Admin panel"
    )
    
    await message.answer(
        "👨‍💼 **Admin Panel**\n\n"
        "Quyidagi amallardan birini tanlang:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

# ================== YANGI JOY QO'SHISH ==================

@router.message(F.text == "🛠 Avtoservis qo'shish")
@admin_required
async def start_add_autoservice(message: Message, state: FSMContext):
    await state.update_data(place_type="autoservice")
    await message.answer(
        "🛠 **Yangi avtoservis qo'shish**\n\n"
        "Avtoservis nomini kiriting:",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )
    await state.set_state(AddPlace.entering_name)

@router.message(F.text == "🚗 Avtomoyka qo'shish")
@admin_required
async def start_add_carwash(message: Message, state: FSMContext):
    await state.update_data(place_type="carwash")
    await message.answer(
        "🚗 **Yangi avtomoyka qo'shish**\n\n"
        "Avtomoyka nomini kiriting:",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="Markdown"
    )
    await state.set_state(AddPlace.entering_name)

@router.message(AddPlace.entering_name)
@admin_required
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    data = await state.get_data()
    
    place_type = "avtoservis" if data['place_type'] == 'autoservice' else "avtomoyka"
    
    await message.answer(
        f"📍 **{place_type.capitalize()} lokatsiyasini yuboring**\n\n"
        "Telegramdagi 📎 tugmasini bosing va 📍 Lokatsiya ni tanlang, "
        "yoki koordinatalarni shu formatda yuboring:\n"
        "`41.311081, 69.240562`",
        parse_mode="Markdown"
    )
    await state.set_state(AddPlace.entering_location)

@router.message(AddPlace.entering_location)
@admin_required
async def process_location(message: Message, state: FSMContext):
    data = await state.get_data()
    
    if message.location:
        lat = message.location.latitude
        lon = message.location.longitude
    else:
        try:
            coords = message.text.split(',')
            lat = float(coords[0].strip())
            lon = float(coords[1].strip())
        except:
            await message.answer("❌ Noto'g'ri format. Qaytadan kiriting:")
            return
    
    await state.update_data(lat=lat, lon=lon)
    
    place_type = "avtoservis" if data['place_type'] == 'autoservice' else "avtomoyka"
    await message.answer(f"🏠 **{place_type.capitalize()} manzilini kiriting:**", parse_mode="Markdown")
    await state.set_state(AddPlace.entering_address)

@router.message(AddPlace.entering_address)
@admin_required
async def process_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    await message.answer("📞 **Telefon raqamini kiriting:**\n\nMasalan: `+998901234567`", parse_mode="Markdown")
    await state.set_state(AddPlace.entering_phone)

@router.message(AddPlace.entering_phone)
@admin_required
async def process_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    
    data = await state.get_data()
    if data['place_type'] == 'autoservice':
        services_list = "• Elektrik\n• Kasaprab\n• Motarius\n• Vulkanizatsiya\n• Razval\n• Tonirovka\n• Shumka\n• Universal"
    else:
        services_list = "• Tashqi yuvish\n• Ichki tozalash\n• Polirovka\n• Kimyoviy tozalash\n• Dvigatel yuvish\n• Quruq tozalash"
    
    await message.answer(
        f"⚙️ **Xizmatlarni kiriting**\n\n"
        f"Quyidagilardan vergul bilan ajrating:\n{services_list}\n\n"
        f"Masalan: `Elektrik, Motarius, Vulkanizatsiya`",
        parse_mode="Markdown"
    )
    await state.set_state(AddPlace.entering_services)

@router.message(AddPlace.entering_services)
@admin_required
async def process_services(message: Message, state: FSMContext):
    services = [s.strip() for s in message.text.split(',')]
    await state.update_data(services=services)
    
    await message.answer(
        "🕒 **Ish vaqtlarini kiriting**\n\n"
        "Format: `09:00-18:00`\n"
        "Agar 24/7 bo'lsa: `24/7` deb yozing",
        parse_mode="Markdown"
    )
    await state.set_state(AddPlace.entering_hours)

@router.message(AddPlace.entering_hours)
@admin_required
async def process_hours(message: Message, state: FSMContext):
    data = await state.get_data()
    
    if message.text.lower() == '24/7':
        working_hours = {"start": "00:00", "end": "23:59"}
        is_24_7 = True
    else:
        try:
            start, end = message.text.split('-')
            working_hours = {"start": start.strip(), "end": end.strip()}
            is_24_7 = False
        except:
            await message.answer("❌ Noto'g'ri format. Qaytadan kiriting:")
            return
    
    # ID ni avtomatik yaratish
    place_id = f"{data['place_type']}_{data['name'].replace(' ', '_').lower()}"
    
    # Ma'lumotlarni to'plash
    place_data = {
        "id": place_id,
        "name": data["name"],
        "lat": data["lat"],
        "lon": data["lon"],
        "address": data["address"],
        "phone": data["phone"],
        "services": data["services"],
        "working_days": [0, 1, 2, 3, 4, 5],  # Dushanba-Shanba
        "working_hours": working_hours,
        "is_24_7": is_24_7
    }
    
    await state.update_data(place_data=place_data)
    
    # Tasdiqlash
    place_type = "Avtoservis" if data['place_type'] == 'autoservice' else "Avtomoyka"
    working_time = "24/7" if is_24_7 else f"{working_hours['start']} - {working_hours['end']}"
    
    confirmation_text = (
        f"✅ **{place_type} ma'lumotlari**\n\n"
        f"🏷 **Nomi:** {data['name']}\n"
        f"📍 **Manzil:** {data['address']}\n"
        f"📞 **Telefon:** {data['phone']}\n"
        f"🕒 **Ish vaqti:** {working_time}\n"
        f"⚙️ **Xizmatlar:** {', '.join(data['services'])}\n\n"
        f"Ma'lumotlarni saqlaymi?"
    )
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Ha, saqlash"), KeyboardButton(text="❌ Yo'q, bekor qilish")]
        ],
        resize_keyboard=True
    )
    
    await message.answer(confirmation_text, reply_markup=keyboard, parse_mode="Markdown")
    await state.set_state(AddPlace.confirmation)

@router.message(AddPlace.confirmation)
@admin_required
async def process_confirmation(message: Message, state: FSMContext):
    data = await state.get_data()
    
    if message.text == "✅ Ha, saqlash":
        if data['place_type'] == 'autoservice':
            success = await insert_autoservice(data['place_data'])
            place_type = "avtoservis"
        else:
            success = await insert_carwash(data['place_data'])
            place_type = "avtomoyka"
        
        if success:
            await message.answer(f"✅ {place_type.capitalize()} muvaffaqiyatli qo'shildi!", reply_markup=ReplyKeyboardRemove())
        else:
            await message.answer(f"❌ {place_type.capitalize()} qo'shishda xatolik!", reply_markup=ReplyKeyboardRemove())
    
    else:
        await message.answer("❌ Bekor qilindi.", reply_markup=ReplyKeyboardRemove())
    
    await state.clear()
    await admin_panel(message)  # Admin panelga qaytish

# ================== RO'YXATLARNI KO'RISH ==================

@router.message(F.text == "📋 Avtoservislar ro'yxati")
@admin_required
async def show_autoservices(message: Message):
    services = await get_all_autoservices()
    
    if not services:
        await message.answer("❌ Avtoservislar topilmadi.")
        return
    
    text = "🛠 **Avtoservislar ro'yxati:**\n\n"
    for i, service in enumerate(services, 1):
        text += f"{i}. **{service['name']}**\n"
        text += f"   📍 {service['address']}\n"
        text += f"   📞 {service['phone']}\n"
        text += f"   🆔 {service['id']}\n\n"
    
    await message.answer(text, parse_mode="Markdown")

@router.message(F.text == "📋 Avtomoykalar ro'yxati")
@admin_required
async def show_carwashes(message: Message):
    carwashes = await get_all_carwashes()
    
    if not carwashes:
        await message.answer("❌ Avtomoykalar topilmadi.")
        return
    
    text = "🚗 **Avtomoykalar ro'yxati:**\n\n"
    for i, carwash in enumerate(carwashes, 1):
        text += f"{i}. **{carwash['name']}**\n"
        text += f"   📍 {carwash['address']}\n"
        text += f"   📞 {carwash['phone']}\n"
        text += f"   🆔 {carwash['id']}\n\n"
    
    await message.answer(text, parse_mode="Markdown")

# ================== O'CHIRISH ==================

@router.message(F.text == "🗑 Avtoservis o'chirish")
@admin_required
async def delete_autoservice_handler(message: Message):
    services = await get_all_autoservices()
    
    if not services:
        await message.answer("❌ O'chirish uchun avtoservislar topilmadi.")
        return
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=f"🗑 {service['name']}")] for service in services] +
                 [[KeyboardButton(text="🔙 Orqaga")]],
        resize_keyboard=True
    )
    
    await message.answer("🗑 **O'chirish uchun avtoservisni tanlang:**", reply_markup=keyboard, parse_mode="Markdown")

@router.message(F.text.startswith("🗑 "))
@admin_required
async def process_delete_autoservice(message: Message):
    service_name = message.text[2:]  # "🗑 " ni olib tashlaymiz
    
    services = await get_all_autoservices()
    service_to_delete = None
    
    for service in services:
        if service['name'] == service_name:
            service_to_delete = service
            break
    
    if service_to_delete:
        success = await delete_autoservice(service_to_delete['id'])
        if success:
            await message.answer(f"✅ '{service_name}' muvaffaqiyatli o'chirildi!")
        else:
            await message.answer(f"❌ '{service_name}' o'chirishda xatolik!")
    else:
        await message.answer("❌ Avtoservis topilmadi.")
    
    await admin_panel(message)

@router.message(F.text == "🗑 Avtomoyka o'chirish")
@admin_required
async def delete_carwash_handler(message: Message):
    carwashes = await get_all_carwashes()
    
    if not carwashes:
        await message.answer("❌ O'chirish uchun avtomoykalar topilmadi.")
        return
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=f"🗑 {carwash['name']}")] for carwash in carwashes] +
                 [[KeyboardButton(text="🔙 Orqaga")]],
        resize_keyboard=True
    )
    
    await message.answer("🗑 **O'chirish uchun avtomoykani tanlang:**", reply_markup=keyboard, parse_mode="Markdown")

# ================== STATISTIKA ==================

@router.message(F.text == "📊 Statistika")
@admin_required
async def show_stats(message: Message):
    autoservices = await get_all_autoservices()
    carwashes = await get_all_carwashes()
    
    text = (
        "📊 **Statistika**\n\n"
        f"🛠 Avtoservislar: {len(autoservices)} ta\n"
        f"🚗 Avtomoykalar: {len(carwashes)} ta\n"
        f"📈 Jami: {len(autoservices) + len(carwashes)} ta"
    )
    
    await message.answer(text, parse_mode="Markdown")

# ================== ADMIN PANELDAN CHIQISH ==================

@router.message(F.text == "🚪 Admin paneldan chiqish")
@admin_required
async def exit_admin_panel(message: Message):
    await message.answer(
        "👋 Admin paneldan chiqildi. Endi oddiy foydalanuvchi rejimidasiz.",
        reply_markup=ReplyKeyboardRemove()
    )
