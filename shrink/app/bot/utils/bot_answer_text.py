import json


def get_text_by_key(key: str) -> str:
    with open("app/bot/files/texts.json") as f:
        data = json.load(f)

        return data[key]


def get_greeting(first_name: str) -> str:
    return get_text_by_key("greeting").format(first_name=first_name)


def get_registration_info() -> str:
    return get_text_by_key("registration_info")


def get_profile_content(first_name: str, email: str, premium) -> str:
    return get_text_by_key("profile_content")
    

def get_support_answer() -> str:
    return get_text_by_key("support")


def get_not_registered() -> str:
    return get_text_by_key("not_registered")


def get_mailing_registration_required() -> str:
    return get_text_by_key("mailing_registration")


def get_quit_profile() -> str:
    with open("app/bot/files/quit_profile.html") as html:
        return html.read()


def get_how_the_bot_works() -> str:
    return get_text_by_key("how_the_bot_works")


def get_reg_start_info() -> str:
    return get_text_by_key("registration_start_info")


def get_without_sub_info() -> str:
    return get_text_by_key("without_subscription_info")


def get_basic_sub_info() -> str:
    return get_text_by_key("basic_subscription_info")


def get_premium_sub_info() -> str:
    return get_text_by_key("premium_subscription_info")


def get_basic_subscription_price() -> str:
    return get_text_by_key("basic_subscription_price")


def get_premium_subscription_price() -> str:
    return get_text_by_key("premium_subscription_price")


def get_wait_email_addresses_text() -> str:
    return get_text_by_key("wait_to_send_email_addresses")


def get_pre_quit_text() -> str:
    return get_text_by_key("pre_quit_text")


def get_quantity_text() -> str:
    return get_text_by_key("quantity")


def get_email_subject_text() -> str:
    return get_text_by_key("email_subject_text")


def get_email_scheduler_time() -> str:
    return get_text_by_key("email_scheduler_time")


def get_add_audio_text() -> str:
    return get_text_by_key("add_audio_text")


def get_del_audio_text() -> str:
    return get_text_by_key("del_audio_text")


def get_auto_mailing_choice_text() -> str:
    return get_text_by_key("auto_mailing_choice_text")


def get_auto_mailing_settings_info(settings_info: str) -> str:
    return get_text_by_key("auto_mailing_settings_info").format(settings_info[0], settings_info[1], settings_info[2], settings_info[3])


def get_support_screen() -> str:
    return get_text_by_key("support_screen_text")


def get_user_complaint_content(state_data: str) -> str:
    return get_text_by_key("user_complain_content").format(state_data=state_data['text'])


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
    return get_text_by_key("user_email_addresses_text").format(emails=email_list)     


def get_if_wrong_password() -> str:
    return get_text_by_key("wrong_password_text")
