import re


def parse_emails(input_string: str) -> list[str]:
    # Разбиваем строку на адреса по запятой или символам новой строки
    emails = [email.strip() for email in re.split(r'[,\n]', input_string) if email.strip()]

    return emails
