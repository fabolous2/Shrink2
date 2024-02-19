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