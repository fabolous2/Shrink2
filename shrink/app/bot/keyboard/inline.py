from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

def create_inline_button(text: str, callback_data: str, url: str | None = None) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=text, callback_data=callback_data, url=url)

def create_inline_keyboard(*rows: list[InlineKeyboardButton]) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=list(rows))

# Определение кнопок

subscription_types_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='🥇 Premium', callback_data="premium_type"),
        ],
        [
            InlineKeyboardButton(text='🥈 Basic', callback_data="basic_type"),
        ]
    ]
)

again_searching_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="🔎 Найти заного.", callback_data="subscription_issuing")
        ]
    ]
)

duration_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="1 месяц", callback_data="one_month_subscription")
        ],
        [
            InlineKeyboardButton(text="3 месяца", callback_data="three_months_subscription")
        ],
        [
            InlineKeyboardButton(text="6 месяцов", callback_data="six_months_subscription")
        ]
    ]
)

def del_audio_button(unique_id: int) -> InlineKeyboardMarkup:
    button = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='🗑️ Удалить', callback_data=f'delete_audio_extra:{unique_id}'),
                InlineKeyboardButton(text='⬅️ Назад', callback_data='back_to_extra_page')
            ]
        ]
    )
    return button

ok_kb_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="ОK", callback_data="ok")
        ]
    ]
)


back_button = create_inline_button('⬅ Назад', 'main_menu')

registration_button = create_inline_button('📇 Регистрация', 'registration')
repeat_registration_button = create_inline_button('📇 Повторная регистрация', 'repeat_registration')
how_works_be_twin_button = create_inline_button('📖 Как работает Be Twin', 'how_works_be_twin', url="https://telegra.ph/Logistika-i-eyo-sekrety-09-24")

subscription_button = create_inline_button('🎟 Подписка', 'subscription')
more_about_subscription_button = create_inline_button('🗒️ Подробнее о подписках', 'more_about_subscription', url='https://telegra.ph/Podpiska-na-Be-Twin-02-09')

more_about_subscription_button_in_profile = create_inline_button('🗒️ О подписках', 'more_about_subscription',
                                                      url='https://telegra.ph/Podpiska-na-Be-Twin-02-09')
cancel_subscription_button = create_inline_button('📉 Отменить подписку', 'sub_cancel')
have_questions_button = create_inline_button('📝 Остались вопросы?', 'have_questions', url='https://t.me/urtwin6')

extra_mailing_type_button = create_inline_button('EХTRA', 'self_mailing')
auto_mailing_type_button = create_inline_button('AUTO', 'auto_mailing')

seven_pm_button = create_inline_button("19:00", "seven_pm")
eight_pm_button = create_inline_button("20:00", "eight_pm")
nine_pm_button = create_inline_button("21:00", "nine_pm")
ten_pm_button = create_inline_button("22:00", "ten_pm")
five_min_after = create_inline_button("+5 минут", "pm")


two_audio_amount = create_inline_button("2", "two_audio_amount")
three_audio_amount = create_inline_button("3", "three_audio_amount")
four_audio_amount = create_inline_button("4", "four_audio_amount")
five_audio_amount = create_inline_button("5", "five_audio_amount")

def add_beats_to_state(times: int) -> InlineKeyboardButton:
    kb = InlineKeyboardButton(text='🎹 Добавить биты', callback_data=f"add_to_db:{times}")
    return kb
add_beats_to_state_an = create_inline_button('🎹 Добавить биты', "add_to_db")
send_from_state = create_inline_button("📮 Отправить", "send_from_db")
delete_audio_state = create_inline_button("🗑️ Удалить биты", "del_audio_from_db")


one_day_frequency = create_inline_button("ежедневно", "one_day_frequency")
two_day_frequency = create_inline_button("раз в 2 дня", "two_day_frequency")
three_day_frequency = create_inline_button("раз в 3 дня", "three_day_frequency")
four_day_frequency = create_inline_button("раз в 4 дня", "four_day_frequency")

support_button = create_inline_button("👨‍💻 Поддержка", "support")
without_subj_button = create_inline_button("🚫 Без заголовка", "without_subject")
without_desc_button = create_inline_button("🚫 Без текста", "without_desc")

without_subj_for_extra_button = create_inline_button("🚫 Без заголовка", "without_subject_for_extra")
without_desc_for_extra_button = create_inline_button("🚫 Без текста", "without_desc_for_extra")

back_to_auto_button = create_inline_button("⬅️ Назад", "settings")

profile_button = create_inline_button('🧸 Профиль', 'profile')
pre_log_out_button = create_inline_button("🏃🏻 Выйти", "pre_quit")
back_to_profile_button = create_inline_button("⬅️ Назад", "profile")
back_to_log_out_menu_button = create_inline_button("⬅️ Назад", "profile")
log_out_for_sure_button = create_inline_button("✅ Выйти", "quit")
back_to_main_menu_button = create_inline_button("⬅️ Назад", "main_menu")
change_user_profile_button = create_inline_button("👣 Выйти", "pre_quit")

auto_mailing_add_email_button = create_inline_button("✉️ Почты", "add_emails")
auto_mailing_add_audio_button = create_inline_button("🎹 Биты", "add_audio")
auto_mailing_settings_button = create_inline_button("⚙️ Настройки", "settings")

back_from_update_message = create_inline_button("⚙️ Вернуться", "settings")

set_subject_button = create_inline_button("📋 Заголовок письма", "set_email_content")
set_description_button = create_inline_button("📄 Текст письма", "set_description")
set_frequency_button = create_inline_button("🗓 Периодичность отправки", "set_frequency")
set_email_scheculer_button = create_inline_button("⏰ Время отправки", "set_scheduler")
set_audio_quantity_button = create_inline_button("🔉 Количество аудио в одном письме", "set_quantity")

mailing_for_admin = create_inline_button("📪 Рассылка", "newsletter")
subscription_issuing_button = create_inline_button("🎫 Выдать подписку", "subscription_issuing")

premium_subscription_choice_button = create_inline_button("🥇premium", "premium")
basic_subscription_choice_button = create_inline_button("🥈basic", "basic")
subscription_choice_free_button = create_inline_button('💳 Оформить подписку','purchase_subscription')
subscription_choice_prem_button = create_inline_button('♻️ Изменить подписку','change_subscription')

change_sub_to_prem = create_inline_button('♻️ Изменить', 'change_sub_to_prem')
change_sub_to_basic = create_inline_button('♻️ Изменить', 'change_sub_to_basic')
back_to_sub_menu = create_inline_button('⬅️ Назад','subscription')


ukassa_payment_button = create_inline_button("ЮKassa", "ukassa_call")
freekassa_payment_button = create_inline_button("FreeKassa", "freekassa_call")
back_to_choice_subscription_button = create_inline_button("⬅ Назад", "back_to_subscriptions_choice")

ukassa_one_month_subscription_button = create_inline_button("1 month subscription", "ukassa_1_sub")
ukassa_three_months_subscription_button = create_inline_button("3 months subscription", "ukassa_3_sub")
ukassa_six_months_subscription_button = create_inline_button("6 months subscription", "ukassa_6_sub")

premium_one_month_subscription_button = create_inline_button("1 month subscription", "premium_1_sub")
premium_three_months_subscription_button = create_inline_button("3 months subscription", "premium_3_sub")
premium_six_months_subscription_button = create_inline_button("6 months subscription", "premium_6_sub")

basic_one_month_subscription_button = create_inline_button("1 month subscription", "basic_1_sub")
basic_three_months_subscription_button = create_inline_button("3 months subscription", "basic_3_sub")
basic_six_months_subscription_button = create_inline_button("6 months subscription", "basic_6_sub")


freekassa_one_month_subscription_button = create_inline_button("1 month subscription", "freekassa_1_sub")
freekassa_three_months_subscription_button = create_inline_button("3 months subscription", "freekassa_3_sub")
freekassa_six_months_subscription_button = create_inline_button("6 months subscription", "freekassa_6_sub")

confirm_compaints_sending_button = create_inline_button("✅ Подтвердить", "confirm_complaint")
cancel_complaints_sending_button = create_inline_button("🗑️ Отмена", "cancel_complaint")
complaint_sending_without_screen_button = create_inline_button("📮 Отправить сейчас", "send_complaint_without_screen")

back_to_settings_menu = create_inline_button("⬅ Назад", "auto_mailing")

delete_emails_button = create_inline_button("🗑️ Удалить", "delete_emails")
add_emails_button = create_inline_button("✉️ Пополнить", "add_emails_to_db")
view_current_email_list = create_inline_button("✉️ Смотреть актуальный список", "add_emails")

delete_audio_button = create_inline_button("🗑️ Удалить", "del_audio")
add_audio_button = create_inline_button("🎹 Пополнить", "add_audio_to_db")
view_current_audio_list = create_inline_button("🎹 Смотреть актуальный список", "add_audio")
view_current_audio_list_from_extra = create_inline_button("🎹 Смотреть актуальный список", "add_audio_to_extra")

turn_on_auto_mailing_button = create_inline_button("🟩 Включить AUTO", "turn_on_mailing")
turn_off_auto_mailing_button = create_inline_button("🟥 Выключить AUTO", "turn_off_mailing")



# Определение клавиатур
profile_inline_kb_markup = create_inline_keyboard([registration_button], [back_button])
profile_repeat_registration_kb_markup = create_inline_keyboard([repeat_registration_button])
reg_for_first_time_mailing_kb_markup = create_inline_keyboard([registration_button], [how_works_be_twin_button])
how_works_be_twin_kb_markup = create_inline_keyboard([how_works_be_twin_button])
main_menu_inline_kb_markup = create_inline_keyboard([profile_button], [subscription_button], [how_works_be_twin_button])
subscription_menu_kb_markup = create_inline_keyboard([subscription_choice_free_button],
                                                     [more_about_subscription_button], [back_to_main_menu_button])
cancel_subscription_kb_markup = create_inline_keyboard([subscription_choice_prem_button], [more_about_subscription_button], [back_to_main_menu_button])
registration_mailing_kb_markup = create_inline_keyboard([repeat_registration_button], [how_works_be_twin_button])
have_questions_kb_markup = create_inline_keyboard([have_questions_button])
choose_mailing_type_kb_markup = create_inline_keyboard([extra_mailing_type_button, auto_mailing_type_button])
quit_profile_kb_markup = create_inline_keyboard([pre_log_out_button], [back_to_profile_button])
logout_for_sure_markup = create_inline_keyboard([log_out_for_sure_button], [back_to_log_out_menu_button])
back_to_main_menu_markup = create_inline_keyboard([back_to_main_menu_button])
change_profile_markup = create_inline_keyboard([change_user_profile_button], [more_about_subscription_button_in_profile], [back_to_main_menu_button])
choose_email_action_markup = create_inline_keyboard([add_emails_button], [delete_emails_button])
add_emails_to_list_markup = create_inline_keyboard([add_emails_button], [back_to_settings_menu])
choose_auto_mailing_actions_markup = create_inline_keyboard([auto_mailing_add_email_button, auto_mailing_add_audio_button],
                                                            [auto_mailing_settings_button])
turned_on_settings_choice_markup = create_inline_keyboard(
                                                [set_subject_button, set_description_button],
                                                [set_frequency_button, set_email_scheculer_button],                                           
                                                [set_audio_quantity_button, turn_on_auto_mailing_button], 
                                                [back_to_settings_menu])
turned_off_settings_choice_markup = create_inline_keyboard(
                                                [set_subject_button, set_description_button],
                                                [set_frequency_button, set_email_scheculer_button],                                           
                                                [set_audio_quantity_button, turn_off_auto_mailing_button], 
                                                [back_to_settings_menu])
subscription_choice_markup = create_inline_keyboard([premium_subscription_choice_button, basic_subscription_choice_button], 
                                                    [back_to_sub_menu])
payment_system_choice = create_inline_keyboard([ukassa_payment_button],
                                               [freekassa_payment_button],
                                               [back_to_choice_subscription_button])
ukassa_sub_duration_markup = create_inline_keyboard([ukassa_one_month_subscription_button],
                                                    [ukassa_three_months_subscription_button],
                                                    [ukassa_six_months_subscription_button])
freekassa_sub_duration_markup = create_inline_keyboard([freekassa_one_month_subscription_button],
                                                       [freekassa_three_months_subscription_button],
                                                       [freekassa_six_months_subscription_button])
premium_sub_duration_markup = create_inline_keyboard([premium_one_month_subscription_button],
                                                       [premium_three_months_subscription_button],
                                                       [premium_six_months_subscription_button])
basic_sub_duration_markup = create_inline_keyboard([basic_one_month_subscription_button],
                                                       [basic_three_months_subscription_button],
                                                       [basic_six_months_subscription_button])


complaint_decision_markup = create_inline_keyboard([confirm_compaints_sending_button, cancel_complaints_sending_button])
complaint_sending_without_screen_markup = create_inline_keyboard([complaint_sending_without_screen_button])
premium_subscription_markup = create_inline_keyboard([premium_subscription_choice_button])
basic_subscription_markup = create_inline_keyboard([basic_subscription_choice_button])
cancel_purchase_subscription_markup = create_inline_keyboard([create_inline_button('❌Отменить', 'cancel')])
choose_audio_actions_kb_markup = create_inline_keyboard([add_audio_button], [delete_audio_button]) 
add_audio_kb_markup = create_inline_keyboard([add_audio_button], [back_to_settings_menu])
mailing_for_admin_markup = create_inline_keyboard([mailing_for_admin], [subscription_issuing_button])
frequency_kb_markup = create_inline_keyboard([one_day_frequency, two_day_frequency], [three_day_frequency, four_day_frequency],
                                             [back_to_auto_button])
subject_kb_markup = create_inline_keyboard([without_subj_button], [back_to_auto_button])
desc_kb_markup = create_inline_keyboard([without_desc_button], [back_to_auto_button])

subject_for_extra_kb_markup = create_inline_keyboard([without_subj_for_extra_button])
desc_for_extra_kb_markup = create_inline_keyboard([without_desc_for_extra_button])

schedular_kb_markup = create_inline_keyboard([seven_pm_button, eight_pm_button],
                                             [nine_pm_button, ten_pm_button],
                                             [five_min_after],
                                             [back_to_auto_button])

audio_amount_kb_markup = create_inline_keyboard([two_audio_amount, three_audio_amount],
                                                [four_audio_amount, five_audio_amount], 
                                                [back_to_auto_button])

view_email_list_kb_markup = create_inline_keyboard([view_current_email_list])
view_audio_list_kb_markup = create_inline_keyboard([view_current_audio_list])
view_audio_list_from_extra_kb_markup = create_inline_keyboard([view_current_audio_list_from_extra])

send_from_db_markup = create_inline_keyboard([add_beats_to_state_an, send_from_state])

change_sub_to_prem_kb_markup = create_inline_keyboard([change_sub_to_basic], [back_to_sub_menu])
change_sub_to_basic_kb_markup = create_inline_keyboard([change_sub_to_prem], [back_to_sub_menu])

back_from_update_message_kb_markup = create_inline_keyboard([back_from_update_message])

def paginator_audio(current_page, page_count):
    buttons = []

    if current_page > 0:
        buttons.append(InlineKeyboardButton(text="❮", callback_data=f"pag_audio:prev,{current_page},{page_count}"))
    else:
        buttons.append(InlineKeyboardButton(text="❮", callback_data="null")) 

    # Add page numbering
    page_number = f"{current_page + 1}/{page_count}"
    buttons.append(InlineKeyboardButton(text=page_number, callback_data="null"))

    # Add ">" button if it's not the last page
    if current_page < page_count - 1:
        buttons.append(InlineKeyboardButton(text="❯", callback_data=f"pag_audio:next,{current_page},{page_count}"))
    else:
        buttons.append(InlineKeyboardButton(text="❯", callback_data="null"))

    return [buttons]

def paginator_extra_audio(current_page, page_count):
    buttons = []

    if current_page > 0:
        buttons.append(InlineKeyboardButton(text="❮", callback_data=f"pag_extra_audio:prev,{current_page},{page_count}"))
    else:
        buttons.append(InlineKeyboardButton(text="❮", callback_data="null")) 

    # Add page numbering
    # page_number = f"{current_page + 1}/{page_count}"
    # buttons.append(InlineKeyboardButton(text=page_number, callback_data="null"))

    # Add ">" button if it's not the last page
    if current_page < page_count - 1:
        buttons.append(InlineKeyboardButton(text="❯", callback_data=f"pag_extra_audio:next,{current_page},{page_count}"))
    else:
        buttons.append(InlineKeyboardButton(text="❯", callback_data="null"))

    return [buttons]


def paginator_email(current_page, page_count, pages):
    row = []

    # Добавляем кнопку "Назад"
    if current_page > 0:
        prev_data = f"pag:prev,{current_page},{page_count}"
        row.append(InlineKeyboardButton(text="❮", callback_data=prev_data))
    else:
        row.append(InlineKeyboardButton(text="❮", callback_data="noop", disabled=True))  # Делаем кнопку неактивной

    # Добавляем нумерацию страниц по центру
    page_numbers = f"{current_page + 1}/{page_count}"
    row.append(InlineKeyboardButton(text=page_numbers, callback_data="noop", disabled=True))

    if current_page < page_count - 1:
        next_data = f"pag:next,{current_page},{page_count}"
        row.append(InlineKeyboardButton(text="❯", callback_data=next_data))
    else:
        row.append(InlineKeyboardButton(text="❯", callback_data="noop", disabled=True))  # Делаем кнопку неактивной

    markup = InlineKeyboardMarkup(inline_keyboard=[row])
    return markup