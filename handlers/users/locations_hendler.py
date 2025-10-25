# handlers/users/locations_hendler.py
"""
Handler for location-based queries.

Processes user location to find and display nearby autoservices
and carwashes with detailed information.
"""
from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from typing import List, Dict, Any
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

def format_working_days_compact(working_days_list: List[int]) -> str:
    """
    Format working days in compact format.
    
    Args:
        working_days_list: List of working day numbers (0-6, where 0=Monday)
        
    Returns:
        str: Formatted string showing working days with checkmarks
        Example: "D✅ S✅ Ch✅ P✅ J✅  |  Sh❌ Y❌"
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
    
    # Split into weekdays (Mon-Fri) and weekends (Sat-Sun)
    weekdays = " ".join(days_display[:5])  # Mon-Fri
    weekends = " ".join(days_display[5:])  # Sat-Sun
    
    return f"{weekdays}  |  {weekends}"

def format_services_with_status(available_services: List[str], service_type: str = "autoservice") -> str:
    """
    Format services list with availability status.
    
    Args:
        available_services: List of available service names
        service_type: Type of service ("autoservice" or "carwash")
        
    Returns:
        str: Formatted string with services marked as available (✅) or not (❌)
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

def short_address(address: str, max_words: int = 5) -> str:
    """
    Shorten address to specified number of words.
    
    Args:
        address: Full address string
        max_words: Maximum number of words to keep (default: 5)
        
    Returns:
        str: Shortened address with "..." if truncated
    """
    words = address.split()
    if len(words) > max_words:
        return ' '.join(words[:max_words]) + '...'
    return address

# ================== HANDLERS ==================

@router.message(F.location)
async def get_nearest_places(message: Message) -> None:
    """
    Handle location messages and find nearest places.
    
    Args:
        message: Message containing user's location
    """
    user_id = message.from_user.id
    location = message.location
    
    # Validate location data
    if not location or location.latitude is None or location.longitude is None:
        logger.warning(f"Invalid location data from user {user_id}")
        await message.answer("❌ Noto'g'ri lokatsiya ma'lumoti / Invalid location data")
        return
    
    # Validate coordinates range
    if not (-90 <= location.latitude <= 90) or not (-180 <= location.longitude <= 180):
        logger.warning(f"Invalid coordinates from user {user_id}: {location.latitude}, {location.longitude}")
        await message.answer("❌ Noto'g'ri koordinatalar / Invalid coordinates")
        return
    
    logger.debug(f"Location received: user_id={user_id}")
    logger.debug(f"user_place_type: {user_place_type}")
    
    # Get user's selected place type
    place_type = user_place_type.get(user_id)
    
    if not place_type:
        logger.debug(f"No place_type found for user {user_id}")
        await message.answer("📍 Iltimos, avval servis turini tanlang (avtoservis yoki avtomoyka)")
        return

    logger.debug(f"User {user_id} place_type: {place_type}")
    
    try:
        # Get nearest places from database
        closest_places = await choose_shortest(location, max_results=3, place_type=place_type)
        logger.debug(f"choose_shortest returned {len(closest_places)} places")
    except Exception as e:
        logger.error(f"choose_shortest error: {e}")
        await message.answer("❌ Joylarni topishda xatolik yuz berdi")
        return

    if not closest_places:
        logger.debug("No places found")
        await message.answer("Hech qanday yaqin joy topilmadi 😔")
        return

    logger.debug(f"{len(closest_places)} places found, showing to user...")

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

        logger.debug(f"Place #{index}: {name}, distance: {distance} km")

        # Format information for both service types
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
            # Sanitize phone number (remove invalid characters)
            clean_phone = ''.join(filter(str.isdigit, phone.replace('+', '')))
            if clean_phone:
                buttons.append([
                    InlineKeyboardButton(text="📞 Aloqa", url=f'tg://resolve?phone={clean_phone}'),
                ])
            
        info_keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

        try:
            await message.answer(text, reply_markup=info_keyboard, disable_web_page_preview=False, parse_mode='HTML')
            logger.debug(f"Place #{index} sent to user")
        except Exception as e:
            logger.error(f"Error sending message: {e}")

    if place_type == "carwash":
        await message.answer("✅ Eng yaqin 3 ta avtomoyka ko'rsatildi!", reply_markup=back2)
    else:
        await message.answer("✅ Eng yaqin 3 ta avtoservis ko'rsatildi!", reply_markup=back)
    
    # Remove user from tracking
    user_place_type.pop(user_id, None)
    logger.debug(f"User {user_id} removed from user_place_type")

@router.callback_query(F.data.startswith("geo_id_"))
async def send_geo(call: CallbackQuery) -> None:
    """
    Send geolocation for a selected place.
    
    Args:
        call: Callback query with place ID in data
    """
    await call.answer()
    
    # Parse and validate callback data
    parts = call.data.split("_", 3)
    if len(parts) < 4:
        await call.answer("❌ Ma'lumot xato / Invalid data", show_alert=True)
        return

    place_type, place_id = parts[2], parts[3]
    
    # Validate place_type
    if place_type not in ("autoservice", "carwash"):
        logger.warning(f"Invalid place_type in callback: {place_type}")
        await call.answer("❌ Noto'g'ri ma'lumot / Invalid data", show_alert=True)
        return
    
    place = GEO_CACHE.get(place_type, {}).get(place_id)
    if not place:
        await call.answer("❌ Lokatsiya topilmadi yoki eskirgan ma'lumot / Location not found", show_alert=True)
        return

    lat = place.get("lat")
    lon = place.get("lon")
    if lat is None or lon is None:
        await call.answer("❌ Bu joy uchun koordinata mavjud emas / No coordinates available", show_alert=True)
        return

    try:
        if call.message:
            await call.message.answer_location(latitude=float(lat), longitude=float(lon))
        else:
            await call.answer("❌ Xabar topilmadi / Message not found", show_alert=True)
    except Exception as e:
        logger.error(f"send_geo error: {e}")
        await call.answer("❌ Lokatsiyani yuborishda xatolik / Error sending location", show_alert=True)
