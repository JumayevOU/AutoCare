import re
import uuid
from typing import Optional
from aiogram import F, Router
from aiogram import types
from aiogram.types import (
    Message, CallbackQuery,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
    InlineKeyboardMarkup, InlineKeyboardButton, ContentType
)
from aiogram.fsm.context import FSMContext
from keyboards.inline.menu import categoryMenu
from data.config import ADMIN_GROUP_ID
from loader import dp, bot
from states.hamkorlik_states import PartnershipStates
try:
    from keyboards.default.location_button import back2
except Exception:
    back2 = None

router = Router()
REQUESTS = {}

NAME_REGEX = re.compile(r"^[A-Za-zА-Яа-яЁёҒғҚқЎўҲҳЇїІіЄє'`’\-\s]+$")  
WORKING_DAYS_REGEX = re.compile(r"^[A-Za-zА-Яа-яЁёҒғҚқЎўҲҳЇїІіЄє\-\s,]+$")  
PHONE_DIGITS_REGEX = re.compile(r"\d+")
WORKING_HOURS_REGEX = re.compile(r"^\s*(\d{1,2}):(\d{2})\s*-\s*(\d{1,2}):(\d{2})\s*$")


def validate_name(name: str) -> bool:
    """
    Ism/familiya validatsiyasi: raqam bo'lmasligi, faqat ruxsat etilgan belgilar.
    """
    if not name or not name.strip():
        return False
    name = name.strip()
    if any(ch.isdigit() for ch in name):
        return False
    return bool(NAME_REGEX.match(name))


def normalize_phone(raw_phone: Optional[str]) -> Optional[str]:
    """
    Telefonni tozalaydi va O'zbekiston formatiga keltiradi.
    Yakuniy format: +998XXXXXXXXX
    """
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
    """
    Hafta kunlari (masalan: 'Dushanba-Yakshanba' yoki 'Dushanba,Chorshanba') faqat harf, vergul, tire, bo'sh joy.
    Raqam va boshqa belgilar rad etiladi.
    """
    if not text or not text.strip():
        return False
    text = text.strip()
    if any(ch.isdigit() for ch in text):
        return False
    return bool(WORKING_DAYS_REGEX.match(text))


def validate_working_hours(text: str) -> bool:
    """
    Soat formatini tekshiradi: HH:MM-HH:MM
    - HH 0-23, MM 00-59
    - boshlanish < tugash
    Qo'shimcha: "24/7" formatini ham qabul qiladi.
    """
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
        sh_i = int(sh)
        sm_i = int(sm)
        eh_i = int(eh)
        em_i = int(em)
    except ValueError:
        return False
    if not (0 <= sh_i <= 23 and 0 <= eh_i <= 23 and 0 <= sm_i <= 59 and 0 <= em_i <= 59):
        return False
    start_minutes = sh_i * 60 + sm_i
    end_minutes = eh_i * 60 + em_i
    if start_minutes >= end_minutes:
        return False
    return True


@router.callback_query(F.data == "hamkorlik")
async def start_partnership(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer("🤝 Hamkorlik uchun ariza.\n\nIltimos, ism va familiyangizni kiriting (masalan: Alijon Tursunov):")
    await state.set_state(PartnershipStates.name)


@router.message(PartnershipStates.name, F.text)
async def state_name(message: Message, state: FSMContext):
    name = message.text.strip()
    if not validate_name(name):
        await message.answer(
            "❗️ Ism va familiya noto'g'ri formatda. Iltimos, faqat harflar, bo'sh joy, tire yoki apostrofdan foydalaning — raqam yoki boshqa belgilar kiritilmasin.\n"
            "Masalan: Alijon Tursunov"
        )
        return
    await state.update_data(name=name)
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(KeyboardButton(text="📲 Telefonni kontakt orqali yuborish", request_contact=True))
    kb.add(KeyboardButton(text="✏️ Telefonni yozib yuborish"))
    await message.answer("📞 Iltimos, telefon raqamingizni yuboring (kontakt yoki yozib):", reply_markup=kb)
    await state.set_state(PartnershipStates.phone)


@router.message(PartnershipStates.phone, F.content_type == ContentType.CONTACT)
async def state_phone_contact(message: Message, state: FSMContext):
    contact = message.contact
    phone = contact.phone_number if contact else None
    normalized = normalize_phone(phone)
    if not normalized:
        kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        kb.add(KeyboardButton(text="📲 Telefonni kontakt orqali yuborish", request_contact=True))
        kb.add(KeyboardButton(text="✏️ Telefonni yozib yuborish"))
        await message.answer(
            "❗️ Kontakt orqali kelgan telefon raqami qabul qilinmadi. Iltimos quyidagi formatlardan birida yuboring:\n"
            "- +998901234567\n"
            "- 998901234567\n"
            "- 901234567 (avtomatik +998 qoʻshiladi)\n\nQayta yuboring:",
            reply_markup=kb
        )
        return

    await state.update_data(phone=normalized)
    await message.answer("🏢 Kompaniya nomini kiriting (agar yo‘q bo‘lsa — 'Yo‘q' deb yozing):", reply_markup=ReplyKeyboardRemove())
    await state.set_state(PartnershipStates.company)


@router.message(PartnershipStates.phone, F.text & (F.text != "📲 Telefonni kontakt orqali yubor"))
async def state_phone_text(message: Message, state: FSMContext):
    text = message.text.strip()
    if text == "✏️ Telefonni yozib yuborish":
        await message.answer("Iltimos, telefon raqamingizni yozib yuboring (masalan +998901234567 yoki 901234567):")
        return

    normalized = normalize_phone(text)
    if not normalized:
        kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        kb.add(KeyboardButton(text="📲 Telefonni kontakt orqali yuborish", request_contact=True))
        kb.add(KeyboardButton(text="✏️ Telefonni yozib yuborish"))
        await message.answer(
            "❗️ Telefon raqami noto'g'ri formatda. Iltimos, faqat O'zbekiston (+998) raqamlarini yuboring.\n"
            "Masalan: +998901234567 yoki 901234567 (avtomatik +998 qoʻshiladi).\nQayta yuboring:",
            reply_markup=kb
        )
        return

    await state.update_data(phone=normalized)
    await message.answer("🏢 Kompaniya nomini kiriting (agar yo‘q bo‘lsa — 'Yo‘q' deb yozing):", reply_markup=ReplyKeyboardRemove())
    await state.set_state(PartnershipStates.company)


@router.message(PartnershipStates.company, F.text)
async def state_company(message: Message, state: FSMContext):
    await state.update_data(company=message.text.strip())
    await message.answer("📍 Manzilingizni matn shaklida kiriting (masalan: Sergeli tumani, S. Juraev ko'chasi, 12-uy):")
    await state.set_state(PartnershipStates.address_text)


@router.message(PartnershipStates.address_text, F.text)
async def state_address_text(message: Message, state: FSMContext):
    await state.update_data(address_text=message.text.strip())
    kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(KeyboardButton(text="📍 Geolokatsiya yuborish", request_location=True))
    kb.add(KeyboardButton(text="⛔ Geolokatsiyani o'tkazish"))
    await message.answer("Iloji bo'lsa, aniq joy uchun geolokatsiya ham yuborishingiz mumkin (tavsiya qilinadi).", reply_markup=kb)
    await state.set_state(PartnershipStates.wait_geo)


@router.message(PartnershipStates.wait_geo, F.content_type == ContentType.LOCATION)
async def state_geo_location(message: Message, state: FSMContext):
    loc = message.location
    await state.update_data(geo_lat=loc.latitude, geo_lon=loc.longitude)
    await message.answer("🧾 Qaysi xizmat turlarini taklif qilasiz? (masalan: Dvigatel tamiri, Kuzov, Elektrik):", reply_markup=ReplyKeyboardRemove())
    await state.set_state(PartnershipStates.services)


@router.message(PartnershipStates.wait_geo, F.text & (F.text == "⛔ Geolokatsiyani o'tkazish"))
async def state_geo_skip(message: Message, state: FSMContext):
    await state.update_data(geo_lat=None, geo_lon=None)
    await message.answer("🧾 Qaysi xizmat turlarini taklif qilasiz? (masalan: Dvigatel tamiri, Kuzov, Elektrik):", reply_markup=ReplyKeyboardRemove())
    await state.set_state(PartnershipStates.services)


@router.message(PartnershipStates.wait_geo, F.text)
async def state_geo_other_text(message: Message, state: FSMContext):
    await state.update_data(geo_lat=None, geo_lon=None)
    await state.update_data(address_text=message.text.strip())
    await message.answer("🧾 Qaysi xizmat turlarini taklif qilasiz? (masalan: Dvigatel tamiri, Kuzov, Elektrik):", reply_markup=ReplyKeyboardRemove())
    await state.set_state(PartnershipStates.services)


@router.message(PartnershipStates.services, F.text)
async def state_services(message: Message, state: FSMContext):
    await state.update_data(services=message.text.strip())
    await message.answer("📅 Ish kunlarini kiriting (masalan: Dushanba-Yakshanba yoki Dushanba,Chorshanba,...):")
    await state.set_state(PartnershipStates.working_days)


@router.message(PartnershipStates.working_days, F.text)
async def state_working_days(message: Message, state: FSMContext):
    text = message.text.strip()
    if not validate_working_days(text):
        await message.answer(
            "❗️ Haftaning kunlari noto'g'ri formatda yoki raqam mavjud.\n"
            "Iltimos faqat so'zlar (masalan: Dushanba-Yakshanba yoki Dushanba, Chorshanba) kiriting — raqam kiritmang."
        )
        return
    await state.update_data(working_days=text)
    await message.answer("🕰 Ish soatini kiriting (masalan: 09:00-18:00 yoki 24/7):")
    await state.set_state(PartnershipStates.working_hours)


@router.message(PartnershipStates.working_hours, F.text)
async def state_working_hours(message: Message, state: FSMContext):
    text = message.text.strip()
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
        summary += f"<b>Geolokatsiya:</b> Yo‘q\n"

    summary += (
        f"<b>Xizmatlar:</b> {data.get('services')}\n"
        f"<b>Ish kunlari:</b> {data.get('working_days')}\n"
        f"<b>Ish soati:</b> {data.get('working_hours')}\n\n"
        f"Iltimos ma'lumotni tasdiqlaysizmi?"
    )

    kb_confirm = InlineKeyboardMarkup(row_width=2)
    kb_confirm.add(
        InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="partnership_confirm"),
        InlineKeyboardButton(text="❌ Bekor qilish", callback_data="partnership_cancel"),
    )

    await message.answer(summary, parse_mode="HTML", reply_markup=kb_confirm)
    await state.set_state(PartnershipStates.confirm)


@router.callback_query(F.data == "partnership_confirm", state=PartnershipStates.confirm)
async def partnership_confirm(call: CallbackQuery, state: FSMContext):
    await call.answer()
    data = await state.get_data()
    user_id = call.from_user.id
    user_chat_id = call.message.chat.id
    request_id = uuid.uuid4().hex
    lat = data.get("geo_lat")
    lon = data.get("geo_lon")
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

    kb_admin = InlineKeyboardMarkup(row_width=2)
    kb_admin.add(
        InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"admin_confirm:{request_id}"),
        InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"admin_cancel:{request_id}"),
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
            user_confirm_text += f"<b>Geolokatsiya:</b> Yo‘q\n"

        user_confirm_text += (
            f"<b>Xizmatlar:</b> {data.get('services')}\n"
            f"<b>Ish kunlari:</b> {data.get('working_days')}\n"
            f"<b>Ish soati:</b> {data.get('working_hours')}\n\n"
            f"✅ Tasdiqlangan — admin javobini kuting."
        )

        try:
            await bot.edit_message_text(user_confirm_text, chat_id=call.message.chat.id,
                                        message_id=call.message.message_id, parse_mode="HTML", disable_web_page_preview=True)
        except Exception as e:
            print("Warning: could not edit user's message:", e)
            await call.message.answer("✅ Siz arizangizni tasdiqladingiz. Admin javobini kuting.", reply_markup=ReplyKeyboardRemove())
    except Exception as e:
        print("Error editing user confirm message:", e)

    try:
        sent = await bot.send_message(ADMIN_GROUP_ID, admin_msg_text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=kb_admin)
        REQUESTS[request_id]["admin_message_id"] = sent.message_id
    except Exception as e:
        print("Error sending to admin group (message):", e)
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
        await call.message.answer("✅ Sizning arizangiz adminlarimizga yuborildi. Tez orada ko'rib chiqiladi.", reply_markup=back2 or ReplyKeyboardRemove())
    except Exception:
        pass

    await state.clear()


@router.callback_query(F.data == "partnership_cancel", state=PartnershipStates.confirm)
async def partnership_cancel(call: CallbackQuery, state: FSMContext):
    await call.answer()
    try:
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
    except Exception as e:
        print("Error in partnership_cancel flow:", e)
        try:
            await call.message.answer("❌ Ariza bekor qilindi.\n\n🔁 Davom eting — menyuga qaytish.", reply_markup=categoryMenu)
        except Exception:
            pass

    await state.clear()

    try:
        user_id = call.from_user.id
        to_delete = []
        for rid, val in list(REQUESTS.items()):
            if val.get("user_id") == user_id:
                to_delete.append(rid)
        for rid in to_delete:
            REQUESTS.pop(rid, None)
    except Exception:
        pass


@router.callback_query(lambda c: c.data and c.data.startswith("admin_confirm:"))
async def admin_confirm_handler(call: CallbackQuery):
    await call.answer()
    try:
        if call.message.chat.id != ADMIN_GROUP_ID:
            await call.answer("Bu tugma faqat admin guruhda ishlaydi.", show_alert=True)
            return

        request_id = call.data.split("admin_confirm:", 1)[1]
        req = REQUESTS.get(request_id)
        if not req:
            await call.answer("Bu ariza allaqachon qayta ishlangan yoki topilmadi.", show_alert=True)
            return

        user_chat_id = req["user_chat_id"]
        try:
            await bot.send_message(user_chat_id, "🎉 Sizning hamkorlik arizangiz muvaffaqiyatli tasdiqlandi! Tez orada biz siz bilan bog'lanamiz.")
        except Exception as e:
            print("Error sending confirmation to user:", e)

        admin_msg_id = req.get("admin_message_id")
        admin_chat_id = req.get("admin_chat_id", ADMIN_GROUP_ID)
        admin_text = req.get("admin_message_text", call.message.text or "")
        confirmer = call.from_user.full_name or str(call.from_user.id)
        new_text = admin_text + f"\n\n✅ Ariza tasdiqlandi — <a href='tg://user?id={call.from_user.id}'>{confirmer}</a>"

        try:
            await bot.edit_message_reply_markup(chat_id=admin_chat_id, message_id=admin_msg_id, reply_markup=None)
            await bot.edit_message_text(new_text, chat_id=admin_chat_id, message_id=admin_msg_id, parse_mode="HTML", disable_web_page_preview=True)
        except Exception as e:
            print("Error editing admin message after confirm:", e)

        REQUESTS.pop(request_id, None)

    except Exception as e:
        print("admin_confirm_handler error:", e)
        # aiogram v3: callback_query.answer is async; using call.answer to show alert
        try:
            await call.answer("Xatolik yuz berdi.", show_alert=True)
        except Exception:
            pass


@router.callback_query(lambda c: c.data and c.data.startswith("admin_cancel:"))
async def admin_cancel_handler(call: CallbackQuery):
    await call.answer()
    try:
        if call.message.chat.id != ADMIN_GROUP_ID:
            await call.answer("Bu tugma faqat admin guruhda ishlaydi.", show_alert=True)
            return

        request_id = call.data.split("admin_cancel:", 1)[1]
        req = REQUESTS.get(request_id)
        if not req:
            await call.answer("Bu ariza allaqachon qayta ishlangan yoki topilmadi.", show_alert=True)
            return

        user_chat_id = req["user_chat_id"]
        try:
            await bot.send_message(
                user_chat_id,
                "⚠️ Afsuski, sizning arizangiz hozircha tasdiqlanmadi.\n\n"
                "Iltimos, quyidagilarni tekshirib, arizani qayta yuboring:\n"
                "- Manzil yoki xizmat turi to‘liq va aniq kiritilganmi?\n"
                "- Telefon raqamingiz to‘liq va ishlaydigan raqammi?\n"
                "- Agar iloji bo‘lsa, aniq geolokatsiya yuboring (📍 joy) — bu joyni tasdiqlashni osonlashtiradi.\n\n"
                "Kamchiliklarni tuzatib, menyudan “Hamkorlik” tugmasini bosib, qayta ariza yuboring. Yordam kerak bo‘lsa, murojaat qiling.",
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
            await bot.edit_message_reply_markup(chat_id=admin_chat_id, message_id=admin_msg_id, reply_markup=None)
            await bot.edit_message_text(new_text, chat_id=admin_chat_id, message_id=admin_msg_id, parse_mode="HTML", disable_web_page_preview=True)
        except Exception as e:
            print("Error editing admin message after cancel:", e)

        REQUESTS.pop(request_id, None)

    except Exception as e:
        print("admin_cancel_handler error:", e)
        try:
            await call.answer("Xatolik yuz berdi.", show_alert=True)
        except Exception:
            pass


dp.include_router(router)
