from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Главное меню
main_menu_keyboard_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="📨 Рассылка")
        ],
        [
            KeyboardButton(text="🎡 Главное меню"),
            KeyboardButton(text="‍👨‍💻 Поддержка")
        ],
    ],
    resize_keyboard=True,
    selective=True
)

# Меню рассылки
mailing_menu_keyboard_markup = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Редактировать список почт"),
            KeyboardButton(text="Редактировать список аудио")
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    selective=True
)
