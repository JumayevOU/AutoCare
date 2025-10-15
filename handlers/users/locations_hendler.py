# handlers/users/locations_hendler.py
from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
import logging

from loader import bot
from keyboards.default.location_button import keyboard, back, back2
from utils.misc.get_distance import choose_shortest

router = Router()
logger = logging.getLogger(__name__)

# Cache saqlash uchun
GEO_CACHE = {
    "autoservice": {},
    "carwash": {}
}

WEEK_DAYS_UZ = {
    0: "Dushanba", 1: "Seshanba", 2: "Chorshanba",
    3: "Payshanba", 4: "Juma", 5: "Shanba", 6: "Yakshanba"
}

WEEK_DAYS_SHORT = {
    0: "D", 1: "S", 2: "Ch", 3: "P", 4: "J", 5: "Sh", 6: "Y"
}

# Avtoservice uchun xizmatlar ro'yxati
SERVICE_ORDER = [
    "Elektrik", "Kasaprab", "Motarius", "Vulkanizatsiya",
    "Razval", "Tonirovka", "Shumka", "Universal"
]

# Avtomoyka uchun xizmatlar ro'yxati
CARWASH_SERVICES = [
    "Tashqi yuvish", "Ichki tozalash", "Polirovka", 
    "Kimyoviy tozalash", "Dvigatel yuvish", "Quruq tozalash",
    "Salon tozalash", "Disk tozalash"
]

# Joy turini saqlash uchun user ma'lumotlari
user_place_type = {}

# ================== FUNKSIYALAR ==================

def format_working_days_compact(working_days_list):
    """
    Ish kunlarini qisqa formatda ko'rsatish: D✅ S✅ Ch✅ P✅ J✅ | Sh✅ Y✅
    """
    if not working_days_list:
        return "Ma'lumot yo'q"
    
    days_display = []
    for day_num in range(7):
        day_symbol = WEEK_DAYS_SHORT[day_num]
        if day_num in working_days_list:
            days_display.append(f"{day_symbol}✅")
        else:
            days_display.append(f"{day_symbol}❌")
    
    # Dushanba-Juma va Shanba-Yakshanba guruhlariga ajratamiz
    weekdays = " ".join(days_display[:5])  # D-J
    weekends = " ".join(days_display[5:])  # Sh-Y
    
    return f"{weekdays}  |  {weekends}"

def format_services_with_status(available_services, service_type="autoservice"):
    """
    Xizmatlarni status bilan ko'rsatish: mavjud bo'lsa ✅, yo'q bo'lsa ❌
    """
    services_text = ""
    
    if service_type == "autoservice":
        service_list = SERVICE_ORDER
    else:  # carwash
        service_list = CARWASH_SERVICES
    
    for service in service_list:
        if service in available_services:
            services_text += f"✅ {service}\n"
        else:
            services_text += f"❌ {service}\n"
    return services_text

def short_address(address, max_words=5):
    """
    Manzilni qisqartirish
    """
    words = address.split()
    if len(words) > max_words:
        return ' '.join(words[:max_words]) + '...'
    return address

# ================== HANDLERS ==================

@router.message(F.location)
async def get_nearest_places(message: Message):
    user_id = message.from_user.id
    location = message.location
    
    logger.debug(f"Location qabul qilindi: user_id={user_id}")
    logger.debug(f"user_place_type: {user_place_type}")
    
    # Foydalanuvchi turini olish
    place_type = user_place_type.get(user_id)
    
    if not place_type:
        logger.debug(f"Foydalanuvchi {user_id} uchun place_type topilmadi")
        await message.answer("📍 Iltimos, avval servis turini tanlang (avtoservis yoki avtomoyka)")
        return

    logger.debug(f"Foydalanuvchi {user_id} uchun place_type: {place_type}")
    
    try:
        # Database dan eng yaqin joylarni olish
        closest_places = await choose_shortest(location, max_results=3, place_type=place_type)
        logger.debug(f"choose_shortest {len(closest_places)} ta joy qaytardi")
    except Exception as e:
        logger.error(f"choose_shortest xatosi: {e}")
        await message.answer("❌ Joylarni topishda xatolik yuz berdi")
        return

    if not closest_places:
        logger.debug("Hech qanday joy topilmadi")
        await message.answer("Hech qanday yaqin joy topilmadi 😔")
        return

    logger.debug(f"{len(closest_places)} ta joy topildi, foydalanuvchiga ko'rsatilmoqda...")

    for index, place in enumerate(closest_places, start=1):
        place_id = place.get("id") or f"{place_type}_{index}"
        GEO_CACHE[place_type][place_id] = place

        name = place.get("name", "Noma'lum joy")
        distance = place.get("distance_km", 0.0)
        address = place.get("address", "Manzil yo'q")
        services = place.get("services", []) or []
        working_days = place.get("working_days", [])
        working_hours = place.get("working_hours", {})
        is_24_7 = place.get("is_24_7", False)
        phone = place.get("phone")
        gmaps_url = place.get("gmaps_url", "https://maps.google.com")

        logger.debug(f"Joy #{index}: {name}, masofa: {distance} km")

        # HAR IKKALA TUR UCHUN BIR XIL SHABLON
        addr_short = short_address(address)
        compact_days = format_working_days_compact(working_days)
        services_block = format_services_with_status(services, place_type)
        
        hours_text = "24/7" if is_24_7 else (f"{working_hours.get('start','?')}–{working_hours.get('end','?')}" if working_hours else "Ma'lumot yo'q")

        if place_type == "autoservice":
            text = (
                f"<b>#{index} — {name}</b>\n"
                f"📍 {addr_short} | {distance:.2f} km\n"
                f"🕒 {hours_text} |\n"
                f"📅 {compact_days}\n\n"
                f"────────────────\n"
                f"⚙️ Xizmatlar:\n"
                f"{services_block}"
                f"────────────────"
            )
        else:  # carwash
            text = (
                f"<b>#{index} — {name}</b>\n"
                f"📍 {addr_short} | {distance:.2f} km\n"
                f"🕒 {hours_text} |\n"
                f"📅 {compact_days}\n\n"
                f"────────────────\n"
                f"🧼 Xizmatlar:\n"
                f"{services_block}"
                f"────────────────"
            )

        buttons = [
            [
                InlineKeyboardButton(text="📍 Geolokatsiya", callback_data=f"geo_id_{place_type}_{place_id}"),
                InlineKeyboardButton(text="🗺 Xaritada ochish", url=gmaps_url),
            ]
        ]
        
        if phone:
            # Telefon raqamini to'g'ri formatga keltiramiz
            clean_phone = phone.replace('+', '').replace(' ', '')
            buttons.append([
                InlineKeyboardButton(text="📞 Aloqa", url=f'tg://resolve?phone={clean_phone}'),
            ])
            
        info_keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

        try:
            await message.answer(text, reply_markup=info_keyboard, disable_web_page_preview=False, parse_mode='HTML')
            logger.debug(f"Joy #{index} foydalanuvchiga yuborildi")
        except Exception as e:
            logger.error(f"Xabar yuborishda xatolik: {e}")

    if place_type == "carwash":
        await message.answer("✅ Eng yaqin 3 ta avtomoyka ko'rsatildi!", reply_markup=back2)
    else:
        await message.answer("✅ Eng yaqin 3 ta avtoservis ko'rsatildi!", reply_markup=back)
    
    # Foydalanuvchini ro'yxatdan o'chirish
    user_place_type.pop(user_id, None)
    logger.debug(f"Foydalanuvchi {user_id} user_place_type dan o'chirildi")

@router.callback_query(F.data.startswith("geo_id_"))
async def send_geo(call: CallbackQuery):
    await call.answer()
    parts = call.data.split("_", 3)
    if len(parts) < 4:
        await call.answer("❌ Ma'lumot xato.", show_alert=True)
        return

    place_type, place_id = parts[2], parts[3]
    place = GEO_CACHE.get(place_type, {}).get(place_id)
    if not place:
        await call.answer("❌ Lokatsiya topilmadi yoki eskirgan ma'lumot.", show_alert=True)
        return

    lat = place.get("lat")
    lon = place.get("lon")
    if lat is None or lon is None:
        await call.answer("❌ Bu joy uchun koordinata mavjud emas.", show_alert=True)
        return

    try:
        if call.message:
            await call.message.answer_location(latitude=float(lat), longitude=float(lon))
        else:
            await call.answer("❌ Xabar topilmadi.", show_alert=True)
    except Exception as e:
        logger.error(f"send_geo xatosi: {e}")
        await call.answer("❌ Lokatsiyani yuborishda xatolik yuz berdi.", show_alert=True)
