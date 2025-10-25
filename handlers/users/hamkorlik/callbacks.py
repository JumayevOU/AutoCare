import uuid
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from states.hamkorlik_states import PartnershipStates
from keyboards.inline.menu import categoryMenu
from data.config import ADMIN_GROUP_ID
from loader import bot

from .helpers import (
    build_services_keyboard, build_workdays_keyboard, 
    format_selected_html, SERVICE_OPTIONS, WEEKDAY_OPTIONS,
    prompt_workdays
)

try:
    from keyboards.default.location_button import back2
except ImportError:
    back2 = None

# Import DB functions with fallback
try:
    from database.crud import insert_autoservice, insert_carwash
except ImportError:
    insert_autoservice = None
    insert_carwash = None

# Global requests storage
REQUESTS = {}

def setup_callback_handlers(router: Router):
    """Setup all callback handlers for the router."""
    
    @router.callback_query(PartnershipStates.services, F.data.startswith("svc_toggle:"))
    async def handle_service_toggle(call: CallbackQuery, state: FSMContext):
        """Handle service selection toggle."""
        await call.answer()
        key = call.data.split("svc_toggle:", 1)[1]
        data = await state.get_data()
        selected = set(data.get("services_selected", []))
        
        if key in selected:
            selected.remove(key)
        else:
            selected.add(key)
        
        await state.update_data(services_selected=list(selected))

        selected_text = format_selected_html(selected, SERVICE_OPTIONS)
        base_text = "🧾 Qaysi xizmat turlarini taklif qilasiz?"
        new_text = f"{base_text}\n\n<b>{selected_text}</b>" if selected_text else base_text

        kb = build_services_keyboard(selected)
        try:
            if call.message:
                await call.message.edit_text(new_text, parse_mode="HTML", reply_markup=kb, disable_web_page_preview=True)
        except Exception:
            if call.message:
                await call.message.answer(new_text, parse_mode="HTML", reply_markup=kb)

    @router.callback_query(PartnershipStates.services, F.data == "svc_confirm")
    async def handle_service_confirm(call: CallbackQuery, state: FSMContext):
        """Handle service selection confirmation."""
        await call.answer()
        data = await state.get_data()
        selected = set(data.get("services_selected", []))
        services_str = format_selected_html(selected, SERVICE_OPTIONS) if selected else ""
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

    @router.callback_query(PartnershipStates.working_days, F.data.startswith("wd_toggle:"))
    async def handle_workday_toggle(call: CallbackQuery, state: FSMContext):
        """Handle workday selection toggle."""
        await call.answer()
        key = call.data.split("wd_toggle:", 1)[1]
        data = await state.get_data()
        selected = set(data.get("working_days_selected", []))
        
        if key in selected:
            selected.remove(key)
        else:
            selected.add(key)
        
        await state.update_data(working_days_selected=list(selected))

        selected_text = format_selected_html(selected, WEEKDAY_OPTIONS)
        base_text = "📅 Ish kunlarini kiriting:"
        new_text = f"{base_text}\n\n<b>{selected_text}</b>" if selected_text else base_text

        kb = build_workdays_keyboard(selected)
        try:
            if call.message:
                await call.message.edit_text(new_text, parse_mode="HTML", reply_markup=kb)
        except Exception:
            if call.message:
                await call.message.answer(new_text, parse_mode="HTML", reply_markup=kb)

    @router.callback_query(PartnershipStates.working_days, F.data == "wd_confirm")
    async def handle_workday_confirm(call: CallbackQuery, state: FSMContext):
        """Handle workday selection confirmation."""
        await call.answer()
        data = await state.get_data()
        selected = set(data.get("working_days_selected", []))
        workdays_str = format_selected_html(selected, WEEKDAY_OPTIONS) if selected else ""
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
        except Exception:
            pass
        await state.set_state(PartnershipStates.working_hours)

    @router.callback_query(PartnershipStates.confirm, F.data == "partnership_confirm")
    async def handle_partnership_confirm(call: CallbackQuery, state: FSMContext):
        """Handle partnership confirmation by user."""
        await call.answer()
        data = await state.get_data()
        user_id = call.from_user.id
        user_chat_id = call.message.chat.id if call.message else None
        request_id = uuid.uuid4().hex
        lat = data.get("geo_lat")
        lon = data.get("geo_lon")
        
        # Build admin message
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

        # Send to admin
        try:
            sent = await bot.send_message(ADMIN_GROUP_ID, admin_msg_text, parse_mode="HTML", disable_web_page_preview=True, reply_markup=kb_admin)
            REQUESTS[request_id]["admin_message_id"] = sent.message_id
        except Exception as e:
            print("Error sending to admin group:", e)
            if call.message:
                await call.message.answer("❌ Arizani adminlarga yuborishda xatolik yuz berdi.", reply_markup=back2 or ReplyKeyboardRemove())
            await state.clear()
            REQUESTS.pop(request_id, None)
            return

        # Send location if available
        if lat is not None and lon is not None:
            try:
                await bot.send_location(ADMIN_GROUP_ID, latitude=float(lat), longitude=float(lon))
            except Exception as e:
                print("Error sending location:", e)

        # Confirm to user
        coords_display = coords_line if coords_line else "<b>Geolokatsiya:</b> Yoq\n"
        user_confirm_text = (
            f"<b>🤝 Hamkorlik arizasi (tasdiqlangan)</b>\n\n"
            f"<b>Ism, familiya:</b> {data.get('name')}\n"
            f"<b>Telefon:</b> {data.get('phone')}\n"
            f"<b>Kompaniya:</b> {data.get('company')}\n"
            f"<b>Manzil (matn):</b> {data.get('address_text')}\n"
            f"{coords_display}"
            f"<b>Xizmatlar:</b> {data.get('services')}\n"
            f"<b>Ish kunlari:</b> {data.get('working_days')}\n"
            f"<b>Ish soati:</b> {data.get('working_hours')}\n\n"
            f"✅ Tasdiqlangan — admin javobini kuting."
        )

        try:
            if call.message:
                await bot.edit_message_text(user_confirm_text, chat_id=call.message.chat.id,
                                            message_id=call.message.message_id, parse_mode="HTML", disable_web_page_preview=True)
            await call.message.answer("✅ Sizning arizangiz adminlarimizga yuborildi.", reply_markup=back2 or ReplyKeyboardRemove())
        except Exception:
            if call.message:
                await call.message.answer("✅ Ariza yuborildi.", reply_markup=back2 or ReplyKeyboardRemove())

        await state.clear()

    @router.callback_query(PartnershipStates.confirm, F.data == "partnership_cancel")
    async def handle_partnership_cancel(call: CallbackQuery, state: FSMContext):
        """Handle partnership cancellation by user."""
        await call.answer()
        try:
            if call.message:
                await call.message.answer("❌ Ariza bekor qilindi.\n\n🔁 Davom eting — menyuga qaytish.", reply_markup=categoryMenu)
        except Exception:
            pass

        await state.clear()

    @router.callback_query(F.data.startswith("admin_confirm:"))
    async def handle_admin_confirm(call: CallbackQuery):
        """Handle admin confirmation of partnership request."""
        await call.answer()
        
        if call.message and call.message.chat.id != ADMIN_GROUP_ID:
            await call.answer("Bu tugma faqat admin guruhda ishlaydi.", show_alert=True)
            return

        request_id = call.data.split("admin_confirm:", 1)[1]
        req = REQUESTS.get(request_id)
        if not req:
            await call.answer("Bu ariza allaqachon qayta ishlangan.", show_alert=True)
            return

        # Attempt to save to database
        db_saved = False
        if insert_autoservice is not None:
            try:
                data = req["data"]
                
                # Build name: prefer company if present and not "Yo'q", else name or "Unknown"
                company = data.get('company', '')
                name = data.get('name', 'Unknown')
                if company and company != "Yo'q":
                    entry_name = company
                else:
                    entry_name = name if name else 'Unknown'
                
                # Get lat/lon, fallback to 0.0 if missing
                lat = data.get('geo_lat')
                lon = data.get('geo_lon')
                if lat is None or lon is None:
                    print(f"⚠️ Warning: Missing geo coordinates for request {request_id}, using 0.0")
                    lat = 0.0
                    lon = 0.0
                else:
                    lat = float(lat)
                    lon = float(lon)
                
                # Build services list
                services_list = []
                services_selected = data.get('services_selected', [])
                if services_selected:
                    # Map keys to human-readable labels
                    service_dict = dict(SERVICE_OPTIONS)
                    for key in services_selected:
                        if key in service_dict:
                            services_list.append(service_dict[key])
                else:
                    # Fallback: split services string by comma
                    services_str = data.get('services', '')
                    if services_str:
                        services_list = [s.strip() for s in services_str.split(',') if s.strip()]
                
                # Build working_days list (integer indices 0..6)
                working_days_list = []
                working_days_selected = data.get('working_days_selected', [])
                if working_days_selected:
                    # Map weekday keys to integer indices
                    weekday_dict = {key: idx for idx, (key, _) in enumerate(WEEKDAY_OPTIONS)}
                    for key in working_days_selected:
                        if key in weekday_dict:
                            working_days_list.append(weekday_dict[key])
                
                # Parse working_hours
                working_hours_str = data.get('working_hours', '')
                is_24_7 = False
                working_hours_dict = {}
                if working_hours_str:
                    # Check if 24/7 (case-insensitive, ignore spaces)
                    normalized = working_hours_str.replace(' ', '').lower()
                    if normalized == '24/7':
                        is_24_7 = True
                    elif '-' in working_hours_str:
                        # Parse time range like "09:00-18:00"
                        parts = working_hours_str.split('-', 1)
                        if len(parts) == 2:
                            working_hours_dict = {
                                'start': parts[0].strip(),
                                'end': parts[1].strip()
                            }
                
                # Build DB entry
                entry = {
                    'id': uuid.uuid4().hex,
                    'name': entry_name,
                    'lat': lat,
                    'lon': lon,
                    'address': data.get('address_text'),
                    'phone': data.get('phone'),
                    'services': services_list,
                    'working_days': working_days_list,
                    'working_hours': working_hours_dict,
                    'is_24_7': is_24_7
                }
                
                # Insert into database
                db_saved = await insert_autoservice(entry)
                if db_saved:
                    print(f"✅ Partnership request {request_id} saved to DB successfully")
                else:
                    print(f"⚠️ Failed to save partnership request {request_id} to DB")
                    
            except Exception as e:
                print(f"❌ Error saving partnership request {request_id} to DB: {e}")
                db_saved = False
        else:
            print("⚠️ insert_autoservice not available, skipping DB save")

        # Notify user
        user_chat_id = req["user_chat_id"]
        try:
            if user_chat_id:
                await bot.send_message(user_chat_id, "🎉 Sizning hamkorlik arizangiz muvaffaqiyatli tasdiqlandi! Tez orada biz siz bilan bog'lanamiz.")
        except Exception as e:
            print("Error sending confirmation to user:", e)

        # Update admin message with DB save status
        admin_msg_id = req.get("admin_message_id")
        admin_chat_id = req.get("admin_chat_id", ADMIN_GROUP_ID)
        admin_text = req.get("admin_message_text", "")
        confirmer = call.from_user.full_name or str(call.from_user.id)
        
        # Add DB save status line
        db_status_line = "\n\n💾 Ma'lumotlar DB ga saqlandi." if db_saved else "\n\n⚠️ Ma'lumotlar DB ga saqlanmadi."
        new_text = admin_text + f"\n\n✅ Ariza tasdiqlandi — <a href='tg://user?id={call.from_user.id}'>{confirmer}</a>" + db_status_line

        try:
            if admin_msg_id:
                await bot.edit_message_reply_markup(chat_id=admin_chat_id, message_id=admin_msg_id, reply_markup=None)
                await bot.edit_message_text(new_text, chat_id=admin_chat_id, message_id=admin_msg_id, parse_mode="HTML", disable_web_page_preview=True)
        except Exception as e:
            print("Error editing admin message:", e)

        REQUESTS.pop(request_id, None)

    @router.callback_query(F.data.startswith("admin_cancel:"))
    async def handle_admin_cancel(call: CallbackQuery):
        """Handle admin cancellation of partnership request."""
        await call.answer()
        
        if call.message and call.message.chat.id != ADMIN_GROUP_ID:
            await call.answer("Bu tugma faqat admin guruhda ishlaydi.", show_alert=True)
            return

        request_id = call.data.split("admin_cancel:", 1)[1]
        req = REQUESTS.get(request_id)
        if not req:
            await call.answer("Bu ariza allaqachon qayta ishlangan.", show_alert=True)
            return

        # Notify user
        user_chat_id = req["user_chat_id"]
        try:
            if user_chat_id:
                await bot.send_message(
                    user_chat_id,
                    "⚠️ Afsuski, sizning arizangiz hozircha tasdiqlanmadi.\n\n"
                    "Iltimos, ma'lumotlarni to'ldirib, qayta ariza yuboring.",
                    reply_markup=back2 or ReplyKeyboardRemove()
                )
        except Exception as e:
            print("Error sending cancellation to user:", e)

        # Update admin message
        admin_msg_id = req.get("admin_message_id")
        admin_chat_id = req.get("admin_chat_id", ADMIN_GROUP_ID)
        admin_text = req.get("admin_message_text", "")
        canceller = call.from_user.full_name or str(call.from_user.id)
        new_text = admin_text + f"\n\n❌ Ariza bekor qilindi — <a href='tg://user?id={call.from_user.id}'>{canceller}</a>"

        try:
            if admin_msg_id:
                await bot.edit_message_reply_markup(chat_id=admin_chat_id, message_id=admin_msg_id, reply_markup=None)
                await bot.edit_message_text(new_text, chat_id=admin_chat_id, message_id=admin_msg_id, parse_mode="HTML", disable_web_page_preview=True)
        except Exception as e:
            print("Error editing admin message:", e)

        REQUESTS.pop(request_id, None)