import re
import uuid
from typing import Optional

from aiogram import Router, F, types
from aiogram.types import (
    Message, CallbackQuery,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.fsm.context import FSMContext

from states.hamkorlik_states import PartnershipStates
from keyboards.inline.menu import categoryMenu
from data.config import ADMIN_GROUP_ID
from loader import bot

try:
    from keyboards.default.location_button import back2
except ImportError:
    back2 = None

router = Router()

# ---------- VALIDATSIYA / YORDAMCHI FUNKSIYALAR ----------
REQUESTS = {}

NAME_REGEX = re.compile(r"^[A-Za-zА-Яа-яЁёҒғҚқЎўҲҳЇїІіЄє'`'\-\\s]+$")
WORKING_DAYS_REGEX = re.compile(r"^[A-Za-zА-Яа-яЁёҒғҚқЎўҲҳЇїІіЄє\-\\s,]+$")
PHONE_DIGITS_REGEX = re.compile(r"\d+")
WORKING_HOURS_REGEX = re.compile(r"^\s*(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})\s*$")

SERVICE_OPTIONS = [
    ("elektrik", "⚡ Elektrik"),
    ("kuzov", "🪛 Kuzov tamiri"),
    ("dvigatel", "⚙️ Dvigatel tamiri"),
    ("vulkan", "🛞 Vulkanizatsiya"),
    ("gildirak", "🔍 G'ildirak tekshirish"),
    ("tanirovka", "🪟 Tanirovka"),
    ("shovqun", "🔇 Shovqun izolatsiyasi"),
    ("universal", "🌐 Universal"),
]

WEEKDAY_OPTIONS = [
    ("dushanba", "Dushanba"),
    ("seshanba", "Seshanba"),
    ("chorshanba", "Chorshanba"),
    ("payshanba", "Payshanba"),
    ("juma", "Juma"),
    ("shanba", "Shanba"),
    ("yakshanba", "Yakshanba"),
]

def validate_name(name: str) -> bool:
    if not name or not name.strip():
        return False
    name = name.strip()
    if any(ch.isdigit() for ch in name):
        return False
    return bool(NAME_REGEX.match(name))

def normalize_phone(raw_phone: Optional[str]) -> Optional[str]:
    if not raw_phone:
        return None
    raw = raw_phone.strip()
    plus = raw.startswith("+")
    digits = "".join(re.findall(r"\d", raw))
    if not digits:
        return None
    if len(digits) == 9 and digits[0] == "9":
        return "+998" + digits
    if len(digits) == 12 and digits.startswith("998"):
        return "+" + digits
    if plus and len(digits) == 12 and digits.startswith("998"):
        return "+" + digits
    return None

def validate_working_days(text: str) -> bool:
    if not text or not text.strip():
        return False
    text = text.strip()
    if any(ch.isdigit() for ch in text):
        return False
    return bool(WORKING_DAYS_REGEX.match(text))

def validate_working_hours(text: str) -> bool:
    if not text or not text.strip():
        return False
    clean = text.strip().lower().replace(" ", "")
    if clean == "24/7":
        return True
    m = WORKING_HOURS_REGEX.match(text)
    if not m:
        return False
    sh, sm, eh, em = m.group(1), m.group(2), m.group(3), m.group(4)
    try:
        sh_i = int(sh); sm_i = int(sm); eh_i = int(eh); em_i = int(em)
    except ValueError:
        return False
    if not (0 <= sh_i <= 23 and 0 <= eh_i <= 23 and 0 <= sm_i <= 59 and 0 <= em_i <= 59):
        return False
    start_minutes = sh_i * 60 + sm_i
    end_minutes = eh_i * 60 + em_i
    if start_minutes >= end_minutes:
        return False
    return True

# ---------- INLINE MULTI-SELECT HELPERS ----------
def _format_selected_html(selected_keys, options):
    if not selected_keys:
        return ""
    labels = []
    selected_set = set(selected_keys)
    for key, label in options:
        if key in selected_set:
            parts = label.split(" ", 1)
            labels.append(parts[1] if len(parts) == 2 else label)
    return ", ".join(labels)

def _service_label_for_button(key, selected_set):
    base = dict(SERVICE_OPTIONS)[key]
    if key in selected_set:
        parts = base.split(" ", 1)
        name = parts[1] if len(parts) == 2 else base
        return f"✅ {name}"
    else:
        return base

def _weekday_label_for_button(key, selected_set):
    base = dict(WEEKDAY_OPTIONS)[key]
    if key in selected_set:
        return f"✅ {base}"
    else:
        return base

def build_services_kb(selected_set):
    keyboard = []
    
    # Har 2 ta tugma bir qatorda
    for i in range(0, len(SERVICE_OPTIONS), 2):
        row = []
        for j in range(2):
            if i + j < len(SERVICE_OPTIONS):
                key, _ = SERVICE_OPTIONS[i + j]
                row.append(InlineKeyboardButton(
                    text=_service_label_for_button(key, selected_set),
                    callback_data=f"svc_toggle:{key}"
                ))
        if row:
            keyboard.append(row)
    
    # Tasdiqlash tugmasi
    keyboard.append([InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="svc_confirm")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def build_workdays_kb(selected_set):
    keyboard = []
    
    # Har 2 ta tugma bir qatorda
    for i in range(0, len(WEEKDAY_OPTIONS), 2):
        row = []
        for j in range(2):
            if i + j < len(WEEKDAY_OPTIONS):
                key, _ = WEEKDAY_OPTIONS[i + j]
                row.append(InlineKeyboardButton(
                    text=_weekday_label_for_button(key, selected_set),
                    callback_data=f"wd_toggle:{key}"
                ))
        if row:
            keyboard.append(row)
    
    # Tasdiqlash tugmasi
    keyboard.append([InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="wd_confirm")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

async def prompt_services(message: Message, state: FSMContext):
    await state.update_data(services_selected=[])
    text = "🧾 Qaysi xizmat turlarini taklif qilasiz?"
    kb = build_services_kb(set())
    await message.answer(text, parse_mode="HTML", reply_markup=kb)
    await state.set_state(PartnershipStates.services)

async def prompt_workdays(message_or_call, state: FSMContext):
    await state.update_data(working_days_selected=[])
    text = "📅 Ish kunlarini kiriting:"
    kb = build_workdays_kb(set())
    if isinstance(message_or_call, Message):
        await message_or_call.answer(text, parse_mode="HTML", reply_markup=kb)
    else:
        if message_or_call.message:
            await message_or_call.message.answer(text, parse_mode="HTML", reply_markup=kb)
        else:
            await message_or_call.answer(text, show_alert=True)
    await state.set_state(PartnershipStates.working_days)

# ---------- HANDLERS ----------
@router.callback_query(F.data == "hamkorlik")
async def start_partnership(call: CallbackQuery, state: FSMContext):
    await call.answer()
    if call.message:
        await call.message.answer(
            "🤝 Hamkorlik uchun ariza.\n\nIltimos, ism va familiyangizni kiriting (masalan: Alijon Tursunov):"
        )
    else:
        await call.answer("🤝 Hamkorlik uchun ariza. Iltimos, ism va familiyangizni yuboring.", show_alert=True)
    await state.set_state(PartnershipStates.name)

@router.message(PartnershipStates.name, F.text)
async def state_name(message: Message, state: FSMContext):
    name = (message.text or "").strip()
    if not validate_name(name):
        await message.answer(
            "❗️ Ism va familiya noto'g'ri formatda. Iltimos, faqat harflar, bo'sh joy, tire yoki apostrofdan foydalaning — raqam yoki boshqa belgilar kiritilmasin.\n"
            "Masalan: Alijon Tursunov"
        )
        return
    await state.update_data(name=name)
    
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📲 Telefonni kontakt orqali yuborish", request_contact=True)],
            [KeyboardButton(text="✏️ Telefonni yozib yuborish")]
        ],
        resize_keyboard=True, 
        one_time_keyboard=True
    )
    await message.answer("📞 Iltimos, telefon raqamingizni yuboring (kontakt yoki yozib):", reply_markup=kb)
    await state.set_state(PartnershipStates.phone)

@router.message(PartnershipStates.phone, F.contact)
async def state_phone_contact(message: Message, state: FSMContext):
    contact = message.contact
    phone = contact.phone_number if contact else None
    normalized = normalize_phone(phone)
    if not normalized:
        kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📲 Telefonni kontakt orqali yuborish", request_contact=True)],
                [KeyboardButton(text="✏️ Telefonni yozib yuborish")]
            ],
            resize_keyboard=True, 
            one_time_keyboard=True
        )
        await message.answer(
            "❗️ Kontakt orqali kelgan telefon raqami qabul qilinmadi. Iltimos quyidagi formatlardan birida yuboring:\n"
            "- +998901234567\n"
            "- 998901234567\n"
            "- 901234567 (avtomatik +998 qoʻshiladi)\n\nQayta yuboring:",
            reply_markup=kb
        )
        return

    await state.update_data(phone=normalized)
    await message.answer("🏢 Kompaniya nomini kiriting (agar yo'q bo'lsa — 'Yo'q' deb yozing):", reply_markup=ReplyKeyboardRemove())
    await state.set_state(PartnershipStates.company)

@router.message(PartnershipStates.phone, F.text)
async def state_phone_text(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if text == "📲 Telefonni kontakt orqali yuborish":
        return
    if text == "✏️ Telefonni yozib yuborish":
        await message.answer("Iltimos, telefon raqamingizni yozib yuboring (masalan +998901234567 yoki 901234567):")
        return

    normalized = normalize_phone(text)
    if not normalized:
        kb = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="📲 Telefonni kontakt orqali yuborish", request_contact=True)],
                [KeyboardButton(text="✏️ Telefonni yozib yuborish")]
            ],
            resize_keyboard=True, 
            one_time_keyboard=True
        )
        await message.answer(
            "❗️ Telefon raqami noto'g'ri formatda. Iltimos, faqat O'zbekiston (+998) raqamlarini yuboring.\n"
            "Masalan: +998901234567 yoki 901234567 (avtomatik +998 qoʻshiladi).\nQayta yuboring:",
            reply_markup=kb
        )
        return

    await state.update_data(phone=normalized)
    await message.answer("🏢 Kompaniya nomini kiriting (agar yo'q bo'lsa — 'Yo'q' deb yozing):", reply_markup=ReplyKeyboardRemove())
    await state.set_state(PartnershipStates.company)

@router.message(PartnershipStates.company, F.text)
async def state_company(message: Message, state: FSMContext):
    await state.update_data(company=(message.text or "").strip())
    await message.answer("📍 Manzilingizni matn shaklida kiriting (masalan: Sergeli tumani, S. Juraev ko'chasi, 12-uy):")
    await state.set_state(PartnershipStates.address_text)

@router.message(PartnershipStates.address_text, F.text)
async def state_address_text(message: Message, state: FSMContext):
    await state.update_data(address_text=(message.text or "").strip())
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📍 Geolokatsiya yuborish", request_location=True)],
            [KeyboardButton(text="⛔ Geolokatsiyani o'tkazish")]
        ],
        resize_keyboard=True, 
        one_time_keyboard=True
    )
    await message.answer("Iloji bo'lsa, aniq joy uchun geolokatsiya ham yuborishingiz mumkin (tavsiya qilinadi).", reply_markup=kb)
    await state.set_state(PartnershipStates.wait_geo)

# ---------- GEOLOKATSIYA HANDLERS ----------
@router.message(PartnershipStates.wait_geo, F.location)
async def state_geo_location(message: Message, state: FSMContext):
    loc = message.location
    if loc:
        await state.update_data(geo_lat=loc.latitude, geo_lon=loc.longitude)
    else:
        await state.update_data(geo_lat=None, geo_lon=None)
    await prompt_services(message, state)

@router.message(PartnershipStates.wait_geo, F.text == "⛔ Geolokatsiyani o'tkazish")
async def state_geo_skip(message: Message, state: FSMContext):
    await state.update_data(geo_lat=None, geo_lon=None)
    await prompt_services(message, state)

@router.message(PartnershipStates.wait_geo, F.text)
async def state_geo_other_text(message: Message, state: FSMContext):
    await state.update_data(geo_lat=None, geo_lon=None)
    await state.update_data(address_text=(message.text or "").strip())
    await prompt_services(message, state)

# ---------- INLINE CALLBACKS: SERVICES ----------
@router.callback_query(PartnershipStates.services, F.data.startswith("svc_toggle:"))
async def svc_toggle(call: CallbackQuery, state: FSMContext):
    await call.answer()
    key = call.data.split("svc_toggle:", 1)[1]
    data = await state.get_data()
    selected = set(data.get("services_selected", []))
    if key in selected:
        selected.remove(key)
    else:
        selected.add(key)
    await state.update_data(services_selected=list(selected))

    selected_text = _format_selected_html(selected, SERVICE_OPTIONS)
    base_text = "🧾 Qaysi xizmat turlarini taklif qilasiz?"
    new_text = f"{base_text}\n\n<b>{selected_text}</b>" if selected_text else base_text

    kb = build_services_kb(selected)
    try:
        if call.message:
            await call.message.edit_text(new_text, parse_mode="HTML", reply_markup=kb, disable_web_page_preview=True)
        else:
            await call.answer(new_text, show_alert=True)
    except Exception:
        if call.message:
            await call.message.answer(new_text, parse_mode="HTML", reply_markup=kb)

@router.callback_query(PartnershipStates.services, F.data == "svc_confirm")
async def svc_confirm(call: CallbackQuery, state: FSMContext):
    await call.answer()
    data = await state.get_data()
    selected = set(data.get("services_selected", []))
    services_str = _format_selected_html(selected, SERVICE_OPTIONS) if selected else ""
    await state.update_data(services=services_str)

    base_text = "🧾 Qaysi xizmat turlarini taklif qilasiz?"
    if services_str:
        new_text = f"{base_text}\n\n<b>{services_str}</b>\n\n✅ Tasdiqlangan"
    else:
        new_text = f"{base_text}\n\n<b>Hech narsa tanlanmadi</b>\n\n✅ Tasdiqlangan"

    try:
        if call.message:
            await call.message.edit_text(new_text, parse_mode="HTML", reply_markup=None, disable_web_page_preview=True)
    except Exception:
        pass

    await prompt_workdays(call, state)

# ---------- INLINE CALLBACKS: WORKDAYS ----------
@router.callback_query(PartnershipStates.working_days, F.data.startswith("wd_toggle:"))
async def wd_toggle(call: CallbackQuery, state: FSMContext):
    await call.answer()
    key = call.data.split("wd_toggle:", 1)[1]
    data = await state.get_data()
    selected = set(data.get("working_days_selected", []))
    if key in selected:
        selected.remove(key)
    else:
        selected.add(key)
    await state.update_data(working_days_selected=list(selected))

    selected_text = _format_selected_html(selected, WEEKDAY_OPTIONS)
    base_text = "📅 Ish kunlarini kiriting:"
    new_text = f"{base_text}\n\n<b>{selected_text}</b>" if selected_text else base_text

    kb = build_workdays_kb(selected)
    try:
        if call.message:
            await call.message.edit_text(new_text, parse_mode="HTML", reply_markup=kb)
        else:
            await call.answer(new_text, show_alert=True)
    except Exception:
        if call.message:
            await call.message.answer(new_text, parse_mode="HTML", reply_markup=kb)

@router.callback_query(PartnershipStates.working_days, F.data == "wd_confirm")
async def wd_confirm(call: CallbackQuery, state: FSMContext):
    await call.answer()
    data = await state.get_data()
    selected = set(data.get("working_days_selected", []))
    workdays_str = _format_selected_html(selected, WEEKDAY_OPTIONS) if selected else ""
    await state.update_data(working_days=workdays_str)

    base_text = "📅 Ish kunlarini kiriting:"
    if workdays_str:
        new_text = f"{base_text}\n\n<b>{workdays_str}</b>\n\n✅ Tasdiqlangan"
    else:
        new_text = f"{base_text}\n\n<b>Hech narsa tanlanmadi</b>\n\n✅ Tasdiqlangan"

    try:
        if call.message:
            await call.message.edit_text(new_text, parse_mode="HTML", reply_markup=None)
    except Exception:
        pass

    try:
        if call.message:
            await call.message.answer("🕰 Ish soatini kiriting (masalan: 09:00-18:00 yoki 24/7):")
        else:
            await call.answer("🕰 Ish soatini kiriting (masalan: 09:00-18:00 yoki 24/7):", show_alert=True)
    except Exception:
        pass
    await state.set_state(PartnershipStates.working_hours)

# ---------- WORKING HOURS ----------
@router.message(PartnershipStates.working_hours, F.text)
async def state_working_hours(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if not validate_working_hours(text):
        await message.answer(
            "❗️ Ish soati noto'g'ri formatda yoki soatlar mantiqan xato.\n"
            "To'g'ri misol: 09:00-18:00 (yoki 9:00 - 18:00). Shuningdek 24/7 ham qabul qilinadi."
        )
        return

    await state.update_data(working_hours=text)

    data = await state.get_data()
    summary = (
        f"<b>🤝 Hamkorlik arizasi (sizga ko'rsatish uchun)</b>\n\n"
        f"<b>Ism, familiya:</b> {data.get('name')}\n"
        f"<b>Telefon:</b> {data.get('phone')}\n"
        f"<b>Kompaniya:</b> {data.get('company')}\n"
        f"<b>Manzil (matn):</b> {data.get('address_text')}\n"
    )
    if data.get('geo_lat') is not None and data.get('geo_lon') is not None:
        summary += f"<b>Geolokatsiya (lat,long):</b> {data.get('geo_lat')}, {data.get('geo_lon')}\n"
    else:
        summary += f"<b>Geolokatsiya:</b> Yo'q\n"

    summary += (
        f"<b>Xizmatlar:</b> {data.get('services')}\n"
        f"<b>Ish kunlari:</b> {data.get('working_days')}\n"
        f"<b>Ish soati:</b> {data.get('working_hours')}\n\n"
        f"Iltimos ma'lumotni tasdiqlaysizmi?"
    )

    kb_confirm = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="partnership_confirm"),
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data="partnership_cancel"),
            ]
        ]
    )

    await message.answer(summary, parse_mode="HTML", reply_markup=kb_confirm)
    await state.set_state(PartnershipStates.confirm)

# ---------- USER CONFIRM / CANCEL ----------
@router.callback_query(PartnershipStates.confirm, F.data == "partnership_confirm")
async def partnership_confirm(call: CallbackQuery, state: FSMContext):
    await call.answer()
    data = await state.get_data()
    user_id = call.from_user.id
    user_chat_id = call.message.chat.id if call.message else None
    request_id = uuid.uuid4().hex
    lat = data.get("geo_lat"); lon = data.get("geo_lon")
    coords_line = ""
    maps_link = ""
    if lat is not None and lon is not None:
        coords_line = f"<b>Geolokatsiya (lat,long):</b> {lat}, {lon}\n"
        maps_link = f"https://www.google.com/maps?q={lat},{lon}"

    admin_msg_text = (
        f"<b>🆕 Yangi hamkorlik arizasi (ID: {request_id})</b>\n\n"
        f"<b>Ism, familiya:</b> {data.get('name')}\n"
        f"<b>Telefon:</b> {data.get('phone')}\n"
        f"<b>Kompaniya:</b> {data.get('company')}\n"
        f"<b>Manzil (matn):</b> {data.get('address_text')}\n"
        f"{coords_line}"
        + (f"<b>Xaritada ochish:</b> {maps_link}\n" if maps_link else "")
        + (
            f"<b>Xizmatlar:</b> {data.get('services')}\n"
            f"<b>Ish kunlari:</b> {data.get('working_days')}\n"
            f"<b>Ish soati:</b> {data.get('working_hours')}\n\n"
        )
        + f"<b>Foydalanuvchi:</b> <a href='tg://user?id={user_id}'>Foydalanuvchi</a>\n"
    )

    kb_admin = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"admin_confirm:{request_id}"),
                InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"admin_cancel:{request_id}"),
            ]
        ]
    )

    REQUESTS[request_id] = {
        "data": data,
        "user_id": user_id,
        "user_chat_id": user_chat_id,
        "admin_chat_id": ADMIN_GROUP_ID,
        "admin_message_id": None,
        "admin_message_text": admin_msg_text,
    }

    try:
        user_confirm_text = (
            f"<b>🤝 Hamkorlik arizasi (tasdiqlangan)</b>\n\n"
            f"<b>Ism, familiya:</b> {data.get('name')}\n"
            f"<b>Telefon:</b> {data.get('phone')}\n"
            f"<b>Kompaniya:</b> {data.get('company')}\n"
            f"<b>Manzil (matn):</b> {data.get('address_text')}\n"
        )
        if lat is not None and lon is not None:
            user_confirm_text += f"<b>Geolokatsiya (lat,long):</b> {lat}, {lon}\n"
        else:
            user_confirm_text += f"<b>Geolokatsiya:</b> Yo'q\n"

        user_confirm_text += (
            f"<b>Xizmatlar:</b> {data.get('services')}\n"
            f"<b>Ish kunlari:</b> {data.get('working_days')}\n"
            f"<b>Ish soati:</b> {data.get('working_hours')}\n\n"
            f"✅ Tasdiqlangan — admin javobini kuting."
        )

        try:
            if call.message:
                await bot.edit_message_text(user_confirm_text, chat_id=call.message.chat.id,
                                            message_id=call.message.message_id, parse_mode="HTML", disable_web_page_preview=True)
            else:
                await bot.send_message(user_id, "✅ Siz arizangizni tasdiqladingiz. Admin javobini kuting.")
        except Exception:
            if call.message:
                await call.message.answer("✅ Siz arizangizni tasdiqladingiz. Admin javobini kuting.", reply_markup=ReplyKeyboardRemove())
    except Exception:
        pass

    try:
        sent = await bot.send_message(ADMIN_GROUP_ID, admin_msg_text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=kb_admin)
        REQUESTS[request_id]["admin_message_id"] = sent.message_id
    except Exception as e:
        print("Error sending to admin group (message):", e)
        if call.message:
            await call.message.answer("❌ Arizani adminlarga yuborishda xatolik yuz berdi. Iltimos qaytadan urinib ko'ring.", reply_markup=back2 or ReplyKeyboardRemove())
        await state.clear()
        REQUESTS.pop(request_id, None)
        return

    if lat is not None and lon is not None:
        try:
            await bot.send_location(ADMIN_GROUP_ID, latitude=float(lat), longitude=float(lon))
        except Exception as e:
            print("Error sending location to admin group:", e)

    try:
        if call.message:
            await call.message.answer("✅ Sizning arizangiz adminlarimizga yuborildi. Tez orada ko'rib chiqiladi.", reply_markup=back2 or ReplyKeyboardRemove())
    except Exception:
        pass

    await state.clear()

@router.callback_query(PartnershipStates.confirm, F.data == "partnership_cancel")
async def partnership_cancel(call: CallbackQuery, state: FSMContext):
    await call.answer()
    try:
        if call.message:
            try:
                await bot.edit_message_text("❌ Ariza bekor qilindi.", chat_id=call.message.chat.id,
                                            message_id=call.message.message_id, parse_mode="HTML")
                await call.message.answer("🔁 Davom eting — menyuga qaytish.", reply_markup=categoryMenu)
            except Exception:
                try:
                    await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
                except Exception:
                    pass
                await call.message.answer("❌ Ariza bekor qilindi.\n\n🔁 Davom eting — menyuga qaytish.", reply_markup=categoryMenu)
        else:
            await call.answer("❌ Ariza bekor qilindi. Menyuga qaytish.", show_alert=True)
    except Exception:
        try:
            if call.message:
                await call.message.answer("❌ Ariza bekor qilindi.\n\n🔁 Davom eting — menyuga qaytish.", reply_markup=categoryMenu)
        except Exception:
            pass

    await state.clear()

    try:
        user_id = call.from_user.id
        to_delete = [rid for rid, val in REQUESTS.items() if val.get("user_id") == user_id]
        for rid in to_delete:
            REQUESTS.pop(rid, None)
    except Exception:
        pass

# ---------- ADMIN HANDLERS ----------
@router.callback_query(F.data.startswith("admin_confirm:"))
async def admin_confirm_handler(call: CallbackQuery):
    await call.answer()
    try:
        if call.message and call.message.chat.id != ADMIN_GROUP_ID:
            await call.answer("Bu tugma faqat admin guruhda ishlaydi.", show_alert=True)
            return

        request_id = call.data.split("admin_confirm:", 1)[1]
        req = REQUESTS.get(request_id)
        if not req:
            await call.answer("Bu ariza allaqachon qayta ishlangan yoki topilmadi.", show_alert=True)
            return

        user_chat_id = req["user_chat_id"]
        try:
            if user_chat_id:
                await bot.send_message(user_chat_id, "🎉 Sizning hamkorlik arizangiz muvaffaqiyatli tasdiqlandi! Tez orada biz siz bilan bog'lanamiz.")
        except Exception as e:
            print("Error sending confirmation to user:", e)

        admin_msg_id = req.get("admin_message_id")
        admin_chat_id = req.get("admin_chat_id", ADMIN_GROUP_ID)
        admin_text = req.get("admin_message_text", call.message.text or "")
        confirmer = call.from_user.full_name or str(call.from_user.id)
        new_text = admin_text + f"\n\n✅ Ariza tasdiqlandi — <a href='tg://user?id={call.from_user.id}'>{confirmer}</a>"

        try:
            if admin_msg_id:
                await bot.edit_message_reply_markup(chat_id=admin_chat_id, message_id=admin_msg_id, reply_markup=None)
                await bot.edit_message_text(new_text, chat_id=admin_chat_id, message_id=admin_msg_id, parse_mode="HTML", disable_web_page_preview=True)
        except Exception as e:
            print("Error editing admin message after confirm:", e)

        REQUESTS.pop(request_id, None)

    except Exception as e:
        print("admin_confirm_handler error:", e)
        await call.answer("Xatolik yuz berdi.", show_alert=True)

@router.callback_query(F.data.startswith("admin_cancel:"))
async def admin_cancel_handler(call: CallbackQuery):
    await call.answer()
    try:
        if call.message and call.message.chat.id != ADMIN_GROUP_ID:
            await call.answer("Bu tugma faqat admin guruhda ishlaydi.", show_alert=True)
            return

        request_id = call.data.split("admin_cancel:", 1)[1]
        req = REQUESTS.get(request_id)
        if not req:
            await call.answer("Bu ariza allaqachon qayta ishlangan yoki topilmadi.", show_alert=True)
            return

        user_chat_id = req["user_chat_id"]
        try:
            if user_chat_id:
                await bot.send_message(
                    user_chat_id,
                    "⚠️ Afsuski, sizning arizangiz hozircha tasdiqlanmadi.\n\n"
                    "Iltimos, quyidagilarni tekshirib, arizani qayta yuboring:\n"
                    "- Manzil yoki xizmat turi to'liq va aniq kiritilganmi?\n"
                    "- Telefon raqamingiz to'liq va ishlaydigan raqammi?\n"
                    "- Agar iloji bo'lsa, aniq geolokatsiya yuboring (📍 joy) — bu joyni tasdiqlashni osonlashtiradi.\n\n"
                    "Kamchiliklarni tuzatib, menyudan \"Hamkorlik\" tugmasini bosib, qayta ariza yuboring. Yordam kerak bo'lsa, murojaat qiling.",
                    reply_markup=back2 or ReplyKeyboardRemove()
                )
        except Exception as e:
            print("Error sending cancellation to user:", e)

        admin_msg_id = req.get("admin_message_id")
        admin_chat_id = req.get("admin_chat_id", ADMIN_GROUP_ID)
        admin_text = req.get("admin_message_text", call.message.text or "")
        canceller = call.from_user.full_name or str(call.from_user.id)
        new_text = admin_text + f"\n\n❌ Ariza bekor qilindi — <a href='tg://user?id={call.from_user.id}'>{canceller}</a>"

        try:
            if admin_msg_id:
                await bot.edit_message_reply_markup(chat_id=admin_chat_id, message_id=admin_msg_id, reply_markup=None)
                await bot.edit_message_text(new_text, chat_id=admin_chat_id, message_id=admin_msg_id, parse_mode="HTML", disable_web_page_preview=True)
        except Exception as e:
            print("Error editing admin message after cancel:", e)

        REQUESTS.pop(request_id, None)

    except Exception as e:
        print("admin_cancel_handler error:", e)
        await call.answer("Xatolik yuz berdi.", show_alert=True)