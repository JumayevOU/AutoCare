from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from states.hamkorlik_states import PartnershipStates
from keyboards.inline.menu import categoryMenu
from .validators import validate_name, normalize_phone, validate_working_hours
from .helpers import prompt_services, prompt_workdays, build_confirmation_summary
from .callbacks import setup_callback_handlers

try:
    from keyboards.default.location_button import back2
except ImportError:
    back2 = None

router = Router()

# Setup callback handlers
setup_callback_handlers(router)

@router.callback_query(F.data == "hamkorlik")
async def start_partnership(call: CallbackQuery, state: FSMContext):
    """Start partnership application process."""
    await call.answer()
    if call.message:
        await call.message.answer(
            "🤝 Hamkorlik uchun ariza.\n\nIltimos, ism va familiyangizni kiriting (masalan: Alijon Tursunov):"
        )
    else:
        await call.answer("🤝 Hamkorlik uchun ariza. Iltimos, ism va familiyangizni yuboring.", show_alert=True)
    await state.set_state(PartnershipStates.name)

@router.message(PartnershipStates.name, F.text)
async def handle_name_input(message: Message, state: FSMContext):
    """Handle name input validation."""
    name = (message.text or "").strip()
    if not validate_name(name):
        await message.answer(
            "❗️ Ism va familiya noto'g'ri formatda. Iltimos, faqat harflar, bo'sh joy, tire yoki apostrofdan foydalaning — raqam yoki boshqa belgilar kiritilmasin.\n"
            "Masalan: Alijon Tursunov"
        )
        return
    
    await state.update_data(name=name)
    
    from .helpers import create_phone_keyboard
    kb = create_phone_keyboard()
    await message.answer("📞 Iltimos, telefon raqamingizni yuboring (kontakt yoki yozib):", reply_markup=kb)
    await state.set_state(PartnershipStates.phone)

@router.message(PartnershipStates.phone, F.contact)
async def handle_phone_contact(message: Message, state: FSMContext):
    """Handle phone number input via contact."""
    contact = message.contact
    phone = contact.phone_number if contact else None
    normalized = normalize_phone(phone)
    
    if not normalized:
        from .helpers import create_phone_keyboard
        kb = create_phone_keyboard()
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
async def handle_phone_text(message: Message, state: FSMContext):
    """Handle phone number input via text."""
    text = (message.text or "").strip()
    
    # Handle button presses
    if text in ["📲 Telefonni kontakt orqali yuborish", "✏️ Telefonni yozib yuborish"]:
        if text == "✏️ Telefonni yozib yuborish":
            await message.answer("Iltimos, telefon raqamingizni yozib yuboring (masalan +998901234567 yoki 901234567):")
        return

    normalized = normalize_phone(text)
    if not normalized:
        from .helpers import create_phone_keyboard
        kb = create_phone_keyboard()
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
async def handle_company_input(message: Message, state: FSMContext):
    """Handle company name input."""
    await state.update_data(company=(message.text or "").strip())
    await message.answer("📍 Manzilingizni matn shaklida kiriting (masalan: Sergeli tumani, S. Juraev ko'chasi, 12-uy):")
    await state.set_state(PartnershipStates.address_text)

@router.message(PartnershipStates.address_text, F.text)
async def handle_address_input(message: Message, state: FSMContext):
    """Handle address input."""
    await state.update_data(address_text=(message.text or "").strip())
    
    from .helpers import create_location_keyboard
    kb = create_location_keyboard()
    await message.answer("Iloji bo'lsa, aniq joy uchun geolokatsiya ham yuborishingiz mumkin (tavsiya qilinadi).", reply_markup=kb)
    await state.set_state(PartnershipStates.wait_geo)

@router.message(PartnershipStates.wait_geo, F.location)
async def handle_location_input(message: Message, state: FSMContext):
    """Handle location input."""
    loc = message.location
    if loc:
        await state.update_data(geo_lat=loc.latitude, geo_lon=loc.longitude)
    else:
        await state.update_data(geo_lat=None, geo_lon=None)
    await prompt_services(message, state)

@router.message(PartnershipStates.wait_geo, F.text == "⛔ Geolokatsiyani o'tkazish")
async def handle_location_skip(message: Message, state: FSMContext):
    """Handle location skip."""
    await state.update_data(geo_lat=None, geo_lon=None)
    await prompt_services(message, state)

@router.message(PartnershipStates.wait_geo, F.text)
async def handle_location_other(message: Message, state: FSMContext):
    """Handle other text input during location wait."""
    await state.update_data(geo_lat=None, geo_lon=None)
    await state.update_data(address_text=(message.text or "").strip())
    await prompt_services(message, state)

@router.message(PartnershipStates.working_hours, F.text)
async def handle_working_hours(message: Message, state: FSMContext):
    """Handle working hours input."""
    text = (message.text or "").strip()
    if not validate_working_hours(text):
        await message.answer(
            "❗️ Ish soati noto'g'ri formatda yoki soatlar mantiqan xato.\n"
            "To'g'ri misol: 09:00-18:00 (yoki 9:00 - 18:00). Shuningdek 24/7 ham qabul qilinadi."
        )
        return

    await state.update_data(working_hours=text)
    await build_confirmation_summary(message, state)