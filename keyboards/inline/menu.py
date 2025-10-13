from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


categoryMenu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='🛠️ Avtoservislar', callback_data='avtoservis'),
            InlineKeyboardButton(text='🚿 Avtomoyka', callback_data='moyka'),
        ],
        [
            InlineKeyboardButton(text="🛡️ Bloklashga qarshi tizim", callback_data='security'),
            InlineKeyboardButton(text="⛽ Yoqilg'i yetqazib berish", callback_data='fuel'),
        ],
        [
            InlineKeyboardButton(text="🤝 Hamkorlik", callback_data='hamkorlik'),
        ],
    ])


xizmatlar = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='⚡ Elektrik', callback_data='elektrik'),
            InlineKeyboardButton(text='🪛 Kuzov tamiri', callback_data='kuzov'),
        ],
        [
            InlineKeyboardButton(text="⚙️ Dvigatel tamiri", callback_data='motor'),
            InlineKeyboardButton(text="🛞 Vulkanizatsiya", callback_data='vulkanizatsiya'),
        ],
        [
            InlineKeyboardButton(text="🔍 G'ildirak tekshirish", callback_data='balon'),
            InlineKeyboardButton(text="🪟 Tanirovka", callback_data='tanirovka'),
        ],
        [
            InlineKeyboardButton(text="🔇 Shovqun izolatsiyasi", callback_data='shumka'),
            InlineKeyboardButton(text="🌐 Universal", callback_data='universal'),
        ],
    ])



info = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='📍 Geolokatsiya', callback_data='geolokatsiya'),
        ],
        [
            InlineKeyboardButton(text='📞 Aloqa', url='tg://resolve?phone=998333500155'),
        ],
    ]
)

