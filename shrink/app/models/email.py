from dataclasses import dataclass


@dataclass
class UserEmail:
    email_id: int
    user_id: int
    email_address: str

