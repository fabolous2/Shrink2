from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def create_inline_button(text: str, callback_data: str, url: str | None = None) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=text, callback_data=callback_data, url=url)

def create_inline_keyboard(*rows: list[InlineKeyboardButton]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=list(rows))

# Определение кнопок
registration_button = create_inline_button('📇 Регистрация', 'registration')
back_button = create_inline_button('⬅ Назад', 'main_menu')
repeat_registration_button = create_inline_button('📇 Повторная регистрация', 'repeat_registration')
how_works_be_twin_button = create_inline_button('📖 Как работает Be Twin', 'how_works_be_twin')
profile_button = create_inline_button('🧸 Профиль', 'profile')
subscription_button = create_inline_button('🎟 Подписка', 'subscription')
more_about_subscription_button = create_inline_button('🗒️ Подробнее о подписках', 'more_about_subscription', url='https://telegra.ph/Podpiska-na-Be-Twin-02-09')
cancel_subscription_button = create_inline_button('📉 Отменить подписку', 'sub_cancel')
have_questions_button = create_inline_button('📝 Остались вопросы?', 'have_questions', url='https://t.me/urtwin6')
extra_mailing_type_button = create_inline_button('EXTRA', 'self_mailing')
auto_mailing_type_button = create_inline_button('AUTO', 'auto_mailing')
support_button = create_inline_button("👨‍💻 Поддержка", "support")
pre_log_out_button = create_inline_button("🏃🏻 Выйти", "pre_quit")
back_to_profile_button = create_inline_button("⬅️ Назад", "profile")
back_to_log_out_menu_button = create_inline_button("⬅️ Назад", "quit_profile")
log_out_for_sure_button = create_inline_button("✅ Выйти", "quit")
back_to_main_menu_button = create_inline_button("⬅Back", "main_menu")
change_user_profile_button = create_inline_button("🧬 Сменить профиль", "quit_profile")



# Определение клавиатур
profile_inline_kb_markup = create_inline_keyboard([registration_button], [back_button])
profile_repeat_registration_kb_markup = create_inline_keyboard([repeat_registration_button])
how_works_be_twin_kb_markup = create_inline_keyboard([how_works_be_twin_button])
main_menu_inline_kb_markup = create_inline_keyboard([profile_button], [subscription_button], [how_works_be_twin_button])
subscription_menu_kb_markup = create_inline_keyboard([create_inline_button('💠 Оформить подписку', 'paysystem_purchase_sub')],
                                   [more_about_subscription_button], [back_button])
cancel_subscription_kb_markup = create_inline_keyboard([cancel_subscription_button], [more_about_subscription_button], [back_button])
registration_mailing_kb_markup = create_inline_keyboard([repeat_registration_button], [how_works_be_twin_button])
have_questions_kb_markup = create_inline_keyboard([have_questions_button])
сhoose_mailing_type_kb_markup = create_inline_keyboard([extra_mailing_type_button], [auto_mailing_type_button])
quit_profile_kb_markup = create_inline_keyboard([support_button], [pre_log_out_button], [back_to_profile_button])
log_out_for_sure_markup = create_inline_keyboard([log_out_for_sure_button], [back_to_log_out_menu_button])
back_to_main_menu_markup = create_inline_keyboard([back_to_main_menu_button])
change_profile_markup = create_inline_keyboard([change_user_profile_button], [back_to_main_menu_button])