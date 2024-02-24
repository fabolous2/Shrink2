from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def create_inline_button(text: str, callback_data: str, url: str | None = None) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=text, callback_data=callback_data, url=url)

def create_inline_keyboard(*rows: list[InlineKeyboardButton]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=list(rows))

# Определение кнопок


back_button = create_inline_button('⬅ Назад', 'main_menu')

registration_button = create_inline_button('📇 Регистрация', 'registration')
repeat_registration_button = create_inline_button('📇 Повторная регистрация', 'repeat_registration')
how_works_be_twin_button = create_inline_button('📖 Как работает Be Twin', 'how_works_be_twin')

subscription_button = create_inline_button('🎟 Подписка', 'subscription')
more_about_subscription_button = create_inline_button('🗒️ Подробнее о подписках', 'more_about_subscription',
                                                      url='https://telegra.ph/Podpiska-na-Be-Twin-02-09')
cancel_subscription_button = create_inline_button('📉 Отменить подписку', 'sub_cancel')
have_questions_button = create_inline_button('📝 Остались вопросы?', 'have_questions', url='https://t.me/urtwin6')

extra_mailing_type_button = create_inline_button('EXTRA', 'self_mailing')
auto_mailing_type_button = create_inline_button('AUTO', 'auto_mailing')

support_button = create_inline_button("👨‍💻 Поддержка", "support")

profile_button = create_inline_button('🧸 Профиль', 'profile')
pre_log_out_button = create_inline_button("🏃🏻 Выйти", "pre_quit")
back_to_profile_button = create_inline_button("⬅️ Назад", "profile")
back_to_log_out_menu_button = create_inline_button("⬅️ Назад", "quit_profile")
log_out_for_sure_button = create_inline_button("✅ Выйти", "quit")
back_to_main_menu_button = create_inline_button("⬅Back", "main_menu")
change_user_profile_button = create_inline_button("🧬 Сменить профиль", "quit_profile")

deletion_email_button = create_inline_button("Удалить почту(ы)", "del_email")
addition_email_button = create_inline_button("Добавить почту(ы)", "add_email")

auto_mailing_add_email_button = create_inline_button("✉️ Почты", "add_email")
auto_mailing_add_audio_button = create_inline_button("🎹 Биты", "add_audio")
auto_mailing_settings_button = create_inline_button("⚙️ Настройки", "settings")

set_subject_and_description_button = create_inline_button("Описание+заголовок", "set_email_content")
set_email_scheculer_button = create_inline_button("Время отправки", "set_scheduler")
set_audio_quantity_button = create_inline_button("Кол-во аудио в сообщении", "set_quantity")

premium_subscription_choice_button = create_inline_button("🥇premium", "premium")
basic_subscription_choice_button = create_inline_button("🥈basic", "basic")

ukassa_payment_button = create_inline_button("ЮKassa", "ukassa_call")
freekassa_payment_button = create_inline_button("FreeKassa", "freekassa_call")
back_to_choice_subscription_button = create_inline_button("⬅ Назад", "back_to_subscriptions_choice")

ukassa_one_month_subscription_button = create_inline_button("1 month subscription", "ukassa_1_sub")
ukassa_three_months_subscription_button = create_inline_button("3 months subscription", "ukassa_3_sub")
ukassa_six_months_subscription_button = create_inline_button("6 months subscription", "ukassa_6_sub")

freekassa_one_month_subscription_button = create_inline_button("1 month subscription", "freekassa_1_sub")
freekassa_three_months_subscription_button = create_inline_button("3 months subscription", "freekassa_3_sub")
freekassa_six_months_subscription_button = create_inline_button("6 months subscription", "freekassa_6_sub")

confirm_compaints_sending_button = create_inline_button("✅ Подтвердить", "confirm_complaint")
cancel_complaints_sending_button = create_inline_button("🗑️ Отмена", "cancel_complaint")
complaint_sending_without_screen_button = create_inline_button("📮 Отправить сейчас", "send_complaint_without_screen")


# Определение клавиатур
profile_inline_kb_markup = create_inline_keyboard([registration_button], [back_button])
profile_repeat_registration_kb_markup = create_inline_keyboard([repeat_registration_button])
how_works_be_twin_kb_markup = create_inline_keyboard([how_works_be_twin_button])
main_menu_inline_kb_markup = create_inline_keyboard([profile_button], [subscription_button], [how_works_be_twin_button])
subscription_menu_kb_markup = create_inline_keyboard([create_inline_button('💠 Оформить подписку','purchase_subscription')],
                                                                           [more_about_subscription_button], [back_button])
cancel_subscription_kb_markup = create_inline_keyboard([cancel_subscription_button], [more_about_subscription_button], [back_button])
registration_mailing_kb_markup = create_inline_keyboard([repeat_registration_button], [how_works_be_twin_button])
have_questions_kb_markup = create_inline_keyboard([have_questions_button])
choose_mailing_type_kb_markup = create_inline_keyboard([extra_mailing_type_button], [auto_mailing_type_button])
quit_profile_kb_markup = create_inline_keyboard([support_button], [pre_log_out_button], [back_to_profile_button])
logout_for_sure_markup = create_inline_keyboard([log_out_for_sure_button], [back_to_log_out_menu_button])
back_to_main_menu_markup = create_inline_keyboard([back_to_main_menu_button])
change_profile_markup = create_inline_keyboard([change_user_profile_button], [back_to_main_menu_button])
choose_email_action_markup = create_inline_keyboard([deletion_email_button], [addition_email_button])
add_emails_to_list_markup = create_inline_keyboard([addition_email_button])
choose_auto_mailing_actions_markup = create_inline_keyboard([auto_mailing_add_email_button],
                                                            [auto_mailing_add_audio_button],
                                                            [auto_mailing_settings_button])
settings_choice_markup = create_inline_keyboard([set_subject_and_description_button],
                                                [set_email_scheculer_button],
                                                [set_audio_quantity_button])
subscription_choice_markup = create_inline_keyboard([premium_subscription_choice_button], [basic_subscription_choice_button])
payment_system_choice = create_inline_keyboard([ukassa_payment_button],
                                               [freekassa_payment_button],
                                               [back_to_choice_subscription_button])
ukassa_sub_duration_markup = create_inline_keyboard([ukassa_one_month_subscription_button],
                                                    [ukassa_three_months_subscription_button],
                                                    [ukassa_six_months_subscription_button])
freekassa_sub_duration_markup = create_inline_keyboard([freekassa_one_month_subscription_button],
                                                       [freekassa_three_months_subscription_button],
                                                       [freekassa_six_months_subscription_button])
complaint_decision_markup = create_inline_keyboard([confirm_compaints_sending_button], [cancel_complaints_sending_button])
complaint_sending_without_screen_markup = create_inline_keyboard([complaint_sending_without_screen_button])
premium_subscription_markup = create_inline_keyboard([premium_subscription_choice_button])
basic_subscription_markup = create_inline_keyboard([basic_subscription_choice_button])
cancel_purchase_subscription_markup = create_inline_keyboard([create_inline_button('❌Отменить', 'cancel')])