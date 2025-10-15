from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

keyboard = ReplyKeyboardMarkup(resize_keyboard=True,
                               keyboard=[
                                   [
                                       KeyboardButton(text="📍Joylashuvni yuborish",request_location=True),
                                   ],
                               ])


back = ReplyKeyboardMarkup(resize_keyboard=True,
                               keyboard=[
                                   [
                                       KeyboardButton(text="📚Menyu"),
                                   ],
                                   [
                                       KeyboardButton(text="🔙Ortga")
                                   ]
                               ])


back2 = ReplyKeyboardMarkup(resize_keyboard=True,
                               keyboard=[
                                   [
                                       KeyboardButton(text="📚Menyu"),
                                   ],
                               ])


