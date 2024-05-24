import json
from app.models import EmailSettings


def get_text_by_key(key: str) -> str:
    with open("app/bot/files/texts.json", encoding="utf-8") as f:
        data = json.load(f)

        return data[key]


def get_greeting(first_name: str) -> str:
    return get_text_by_key("greeting").format(first_name=first_name)

 
def get_registration_info() -> str:
    return get_text_by_key("registration_info")


def get_profile_content(first_name: str, email: str, subscription: str) -> str:
    return get_text_by_key("profile_content").format(first_name=first_name, email=email, premium=subscription)
    

def get_support_answer() -> str:
    return get_text_by_key("support")


def get_not_registered() -> str:
    return get_text_by_key("not_registered")


def get_mailing_registration_required() -> str:
    return get_text_by_key("mailing_registration")


def get_quit_profile() -> str:
    return get_text_by_key("after_quit_info_text")


def get_how_the_bot_works() -> str:
    return get_text_by_key("how_the_bot_works")


def get_without_sub_info() -> str:
    return get_text_by_key("without_subscription_info")

def get_user_audio_list() -> str:
    return get_text_by_key("user_audio_list")


def get_basic_sub_info(sub_duration: int) -> str:
    return get_text_by_key("basic_subscription_info").format(sub_duration)


def get_premium_sub_info(sub_duration: int) -> str:
    return get_text_by_key("premium_subscription_info").format(sub_duration)

def get_change_from_basic(sub_duration: int) -> str:
    return get_text_by_key("change_from_basic").format(sub_duration)

def get_change_from_premium(sub_duration: int) -> str:
    return get_text_by_key("change_from_premium").format(sub_duration)


def get_basic_subscription_price() -> str:
    return get_text_by_key("basic_subscription_price")

def get_advice_for_amount() -> str:
    return get_text_by_key("advice_for_amount")

def get_advice_for_frequency() -> str:
    return get_text_by_key("advice_for_frequency")


def get_premium_subscription_price() -> str:
    return get_text_by_key("premium_subscription_price")


def get_wait_email_addresses_text() -> str:
    return get_text_by_key("wait_to_send_email_addresses")


def get_pre_quit_text() -> str:
    return get_text_by_key("pre_quit_text")


def get_quantity_text() -> str:
    return get_text_by_key("quantity_text")


def get_email_subject_text() -> str:
    return get_text_by_key("email_subject_text")

def get_email_description_text() -> str:
    return get_text_by_key("email_description_button")

def get_frequency_button() -> str:
    return get_text_by_key("frequency_button")

def get_description_button_text() -> str:
    return get_text_by_key("email_description_button")


def get_email_scheduler_time() -> str:
    return get_text_by_key("email_scheduler_time")

def get_warning_frequency_text(selected_frequency) -> str:
    return get_text_by_key("warning_frequency_text").format(
        selected_frequency
    )


def get_add_audio_text() -> str:
    return get_text_by_key("add_audio_text")


def get_del_audio_text() -> str:
    return get_text_by_key("del_audio_text")


def get_auto_mailing_choice_text() -> str:
    return get_text_by_key("auto_mailing_choice_text")


def get_auto_mailing_settings_info(settings_info: EmailSettings) -> str:
    email_subject = f"<blockquote>{settings_info.email_subject}</blockquote>" if settings_info.email_subject else f'<u>None</u>'
    email_text = f"<blockquote>{settings_info.email_text}</blockquote>" if settings_info.email_text else f'<u>None</u>'
    amount = f"{settings_info.amount}" if settings_info.amount else '2'
    schedule_time = settings_info.schedule_time.strftime('%H:%M')
    
    frequency = f"{settings_info.frequency}" if settings_info.frequency else f'<u>None</u>'
    if frequency == "1":
        frequency = "ежедневно"
    elif frequency == "2":
        frequency = "раз в 2 дня"
    elif frequency == "3":
        frequency = "раз в 3 дня"
    elif frequency == "4":
        frequency = "раз в 4 дня"
    
    auto_mailing_settings_info_template = get_text_by_key("auto_mailing_settings_info").format(
        email_subject,
        email_text,
        frequency,
        schedule_time,
        amount
    )

    return auto_mailing_settings_info_template
 
def get_support_screen() -> str:
    return get_text_by_key("support_screen_text")


def get_user_complaint_content(state_data: str) -> str:
    return get_text_by_key("user_complain_content").format(state_data=state_data)


def get_successfull_complaint_cancel() -> str:
    return get_text_by_key("successfull_complaint_cancel")


def get_new_user_complaint_text(username: str, user_id: int) -> str:
    return get_text_by_key("new_user_complaint_text").format(username=username, user_id=user_id)


def get_successful_complaint_send() -> str:
    return get_text_by_key("successful_complaint_send")


def get_choose_menu_actions() -> str:
    return get_text_by_key("choose_actions_below_text")


def get_successfull_logout() -> str:
    return get_text_by_key("successfull_logout_text")


def get_user_email_addresses(email_list: str) -> str:
    return get_text_by_key("user_email_addresses_text").format(email_list)

def get_call_support() -> str:
    return get_text_by_key("call_support")      

def get_add_audio(len: int) -> str:
    return get_text_by_key("add_audio").format(len) 

def get_frequency_text(day: int) -> str:
    return get_text_by_key("frequency_text").format(day) 

def get_successful_update_message_text() -> str:
    return get_text_by_key("successful_update_message_text") 

def get_successful_update_value() -> str:
    return get_text_by_key("successful_update_value") 

def get_send_gmail() -> str:
    return get_text_by_key("send_gmail") 

def get_wait_to_del_email_addresses() -> str:
    return get_text_by_key("wait_to_del_email_addresses") 

def get_successful_send_audio() -> str:
    return get_text_by_key("successful_send_audio") 

def get_del_audio(len: int) -> str:
    return get_text_by_key("del_audio").format(len)   

def get_if_wrong_password() -> str:
    return get_text_by_key("wrong_password_text")

def get_empty_audio_list() -> str:
    return get_text_by_key('empty_audio_list')

def get_empty_email_list() -> str:
    return get_text_by_key('empty_email_list')

def get_wrong_user_id() -> str:
    return get_text_by_key('wrong_user_id')

def get_limit_audio_list(limit: int, current_amount: int) -> str:
    return get_text_by_key('limit_audio_list').format(limit, current_amount)

def get_limit_email_list(limit: int, current_amount: int) -> str:
    return get_text_by_key('limit_email_list').format(limit, current_amount)

def get_sub_choice() -> str:
    return get_text_by_key('sub_choice')



def get_extra_menu(subject: str, description: str) -> str:
    subject = f"<blockquote>{subject}</blockquote>" if subject else f'<u>None</u>'
    description = f"<blockquote>{description}</blockquote>" if description else f'<u>None</u>'
    return get_text_by_key('extra_menu').format(subject, description)

def get_main_menu_text() -> str:
    return get_text_by_key('main_menu_text')


def get_choose_type_of_mailing() -> str:
    return get_text_by_key("choose_type_of_mailing")


def get_successful_update_audio() -> str:
    return get_text_by_key("successful_update_audio_text")


def get_wrong_update_audio() -> str:
    return get_text_by_key("wrong_update_audio_text")


def get_invalid_audio_format() -> str:
    return get_text_by_key("invalid_audio_format_text")
