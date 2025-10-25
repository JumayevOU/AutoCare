from aiogram.types import (
    Message, ReplyKeyboardMarkup, KeyboardButton, 
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.fsm.context import FSMContext

from states.hamkorlik_states import PartnershipStates

# Service and weekday options
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

def create_phone_keyboard() -> ReplyKeyboardMarkup:
    """Create phone input keyboard."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📲 Telefonni kontakt orqali yuborish", request_contact=True)],
            [KeyboardButton(text="✏️ Telefonni yozib yuborish")]
        ],
        resize_keyboard=True, 
        one_time_keyboard=True
    )

def create_location_keyboard() -> ReplyKeyboardMarkup:
    """Create location input keyboard."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📍 Geolokatsiya yuborish", request_location=True)],
            [KeyboardButton(text="⛔ Geolokatsiyani o'tkazish")]
        ],
        resize_keyboard=True, 
        one_time_keyboard=True
    )

def format_selected_html(selected_keys, options):
    """Format selected options for HTML display."""
    if not selected_keys:
        return ""
    labels = []
    selected_set = set(selected_keys)
    for key, label in options:
        if key in selected_set:
            parts = label.split(" ", 1)
            labels.append(parts[1] if len(parts) == 2 else label)
    return ", ".join(labels)

def service_label_for_button(key, selected_set):
    """Get service label for button display."""
    base = dict(SERVICE_OPTIONS)[key]
    if key in selected_set:
        parts = base.split(" ", 1)
        name = parts[1] if len(parts) == 2 else base
        return f"✅ {name}"
    else:
        return base

def weekday_label_for_button(key, selected_set):
    """Get weekday label for button display."""
    base = dict(WEEKDAY_OPTIONS)[key]
    if key in selected_set:
        return f"✅ {base}"
    else:
        return base

def build_services_keyboard(selected_set):
    """Build services selection keyboard."""
    keyboard = []
    
    # 2 buttons per row
    for i in range(0, len(SERVICE_OPTIONS), 2):
        row = []
        for j in range(2):
            if i + j < len(SERVICE_OPTIONS):
                key, _ = SERVICE_OPTIONS[i + j]
                row.append(InlineKeyboardButton(
                    text=service_label_for_button(key, selected_set),
                    callback_data=f"svc_toggle:{key}"
                ))
        if row:
            keyboard.append(row)
    
    # Confirmation button
    keyboard.append([InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="svc_confirm")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def build_workdays_keyboard(selected_set):
    """Build workdays selection keyboard."""
    keyboard = []
    
    # 2 buttons per row
    for i in range(0, len(WEEKDAY_OPTIONS), 2):
        row = []
        for j in range(2):
            if i + j < len(WEEKDAY_OPTIONS):
                key, _ = WEEKDAY_OPTIONS[i + j]
                row.append(InlineKeyboardButton(
                    text=weekday_label_for_button(key, selected_set),
                    callback_data=f"wd_toggle:{key}"
                ))
        if row:
            keyboard.append(row)
    
    # Confirmation button
    keyboard.append([InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="wd_confirm")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

async def prompt_services(message: Message, state: FSMContext):
    """Prompt user to select services."""
    await state.update_data(services_selected=[])
    text = "🧾 Qaysi xizmat turlarini taklif qilasiz?"
    kb = build_services_keyboard(set())
    await message.answer(text, parse_mode="HTML", reply_markup=kb)
    await state.set_state(PartnershipStates.services)

async def prompt_workdays(message_or_call, state: FSMContext):
    """Prompt user to select working days."""
    await state.update_data(working_days_selected=[])
    text = "📅 Ish kunlarini kiriting:"
    kb = build_workdays_keyboard(set())
    if hasattr(message_or_call, 'message') and message_or_call.message:
        await message_or_call.message.answer(text, parse_mode="HTML", reply_markup=kb)
    else:
        await message_or_call.answer(text, parse_mode="HTML", reply_markup=kb)
    await state.set_state(PartnershipStates.working_days)

async def build_confirmation_summary(message: Message, state: FSMContext):
    """Build and display confirmation summary."""
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