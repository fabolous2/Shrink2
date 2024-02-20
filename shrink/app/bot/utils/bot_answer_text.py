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

def get_describe_problem_text() -> str:
    return get_text_by_key("describe_the_problem")

def get_pre_quit_text() -> str:
    return get_text_by_key("pre_quit_text")
