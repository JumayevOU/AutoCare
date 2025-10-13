from aiogram import F, Router
from aiogram import types
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ContentType
)
from loader import dp
from keyboards.default.location_button import keyboard, back, back2
from utils.misc.get_distance import choose_shortest

router = Router()

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

SERVICE_ORDER = [
    "Elektrik", "Kasaprab", "Motarius", "Vulkanizatsiya",
    "Razval", "Tonirovka", "Shumka", "Universal"
]


def format_working_days(days_list):
    if not days_list:
        return "Ma'lumot yo'q"
    return ", ".join(WEEK_DAYS_UZ.get(d, str(d)) for d in days_list)


def normalize_days(days_list):
    """
    days_list ga int yoki string kelsa uni int to'plamiga aylantirib qaytaradi.
    """
    if not days_list:
        return set()
    normalized = set()
    for d in days_list:
        if isinstance(d, int):
            normalized.add(d)
        else:
            s = str(d).strip().lower()
            for k, name in WEEK_DAYS_UZ.items():
                if s.startswith(name.lower()) or s.startswith(WEEK_DAYS_SHORT[k].lower()):
                    normalized.add(k)
                    break
    return normalized


def format_compact_days(days_list):
    """
    Compact ko'rinish: 'D✅ S✅ Ch✅ P✅ J✅ | Sh❌ Y❌' kabi
    """
    open_days = normalize_days(days_list)
    left_parts = []
    right_parts = []
    for i in range(0, 5):
        mark = "✅" if i in open_days else "❌"
        left_parts.append(f"{WEEK_DAYS_SHORT[i]}{mark}")
    for i in range(5, 7):
        mark = "✅" if i in open_days else "❌"
        right_parts.append(f"{WEEK_DAYS_SHORT[i]}{mark}")
    return " ".join(left_parts) + "  |  " + " ".join(right_parts)


def format_service_block(available_services):
    """
    available_services — ro'yxat yoki set (case-insensitive).
    Natija: har bir service qatorda ✅ yoki ❌ bilan chiqadi.
    """
    if not available_services:
        available_services = []
    lower_set = {s.strip().lower() for s in available_services}
    lines = []
    for s in SERVICE_ORDER:
        mark = "✅" if s.lower() in lower_set else "❌"
        lines.append(f"{mark} {s}")
    return "\n".join(lines)


def short_address(address):
    """
    Manzilni qisqartirib ko'rsatadi — agar 'Sergeli' bo'lsa uni qaytaradi,
    aks holda agar vergul bilan ajratilgan bo'lsa o'rta qismini oladi, bo'lmasa to'liq manzil.
    """
    if not address:
        return "Manzil yo'q"
    addr = address.lower()
    if "sergeli" in addr:
        return "Sergeli"
    parts = address.split(",")
    if len(parts) >= 2:
        return parts[1].strip()
    return address


@router.callback_query(F.data == "autoservice")
async def show_autoservice_request(call: CallbackQuery):
    await call.message.answer(
        "🛠 Iltimos, joylashuvingizni yuboring (eng yaqin avtoservisni topish uchun):",
        reply_markup=keyboard
    )
    setattr(dp, "current_place_type", "autoservice")
    await call.answer()


@router.callback_query(F.data == "moyka")
async def show_carwash_request(call: CallbackQuery):
    await call.message.answer(
        "🚗 Iltimos, joylashuvingizni yuboring (eng yaqin avtomoykani topish uchun):",
        reply_markup=keyboard
    )
    setattr(dp, "current_place_type", "carwash")
    await call.answer()


@router.message(F.content_type == ContentType.LOCATION)
async def get_nearest_places(message: Message):
    location = message.location
    place_type = getattr(dp, "current_place_type", "autoservice")

    closest_places = choose_shortest(location, max_results=3, place_type=place_type)

    if not closest_places:
        await message.answer("Hech qanday yaqin joy topilmadi 😔")
        return

    for index, place in enumerate(closest_places, start=1):
        place_id = place.get("id") or f"{place_type}_{index}"
        GEO_CACHE[place_type][place_id] = place

        name = place.get("name", "Noma'lum joy")
        distance = place.get("distance_km", 0.0)
        address = place.get("address", "Manzil yo'q")
        services = place.get("services", []) or []
        working_days = place.get("working_days", [])
        wh = place.get("working_hours", {}) or {}
        hours_text = "24/7" if place.get("is_24_7") else (f"{wh.get('start','?')}–{wh.get('end','?')}" if wh else "Ma'lumot yo'q")
        phone = place.get("phone")
        gmaps_url = place.get("gmaps_url")

        if place_type == "autoservice":
            addr_short = short_address(address)
            compact_days = format_compact_days(working_days)
            services_block = format_service_block(services)

            text = (
                f"<b>#{index} — {name}</b>\n"
                f"📍 {addr_short} | {distance:.2f} km\n"
                f"🕒 {hours_text} |\n"
                f"📅 {compact_days}\n\n"
                f"────────────────\n"
                f"⚙️ Xizmatlar:\n"
                f"{services_block}\n"
                f"────────────────"
            )
        else:
            working_days_text = format_working_days(working_days)
            services_joined = ", ".join(services) or "Ma'lumot yo'q"
            text = (
                f"<b>№{index}. {name}</b>\n"
                f"🚗 Sizdan <b>{distance:.2f} km</b> masofada\n"
                f"📍 Manzil: {address}\n"
                f"🧾 Xizmatlar: {services_joined}\n"
                f"⏰ Ish vaqti: {hours_text}\n"
                f"📅 Ish kunlari: {working_days_text}\n"
            )

        buttons = [
            [
                InlineKeyboardButton(text="📍 Geolokatsiya", callback_data=f"geo_id_{place_type}_{place_id}"),
                InlineKeyboardButton(text="🗺 Xaritada ochish", url=gmaps_url if gmaps_url else "https://maps.google.com"),
            ],
            [
                InlineKeyboardButton(text="📞 Aloqa", url=f"tg://resolve?phone={phone}" if phone else "https://t.me"),
            ]
        ]
        info_keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

        await message.answer(text, reply_markup=info_keyboard, disable_web_page_preview=False, parse_mode='HTML')

    if place_type == "carwash":
        await message.answer("✅ Eng yaqin 3 ta avtomoyka ko‘rsatildi!", reply_markup=back2)
    else:
        await message.answer("✅ Eng yaqin 3 ta avtoservis ko‘rsatildi!", reply_markup=back)


@router.callback_query(lambda c: c.data and c.data.startswith("geo_id_"))
async def send_geo(call: CallbackQuery):
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
        await call.message.answer_location(latitude=float(lat), longitude=float(lon))
        await call.answer()
    except Exception as e:
        print("send_geo error:", e)
        await call.answer("❌ Lokatsiyani yuborishda xatolik yuz berdi.", show_alert=True)


dp.include_router(router)
