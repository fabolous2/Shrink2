from enum import Enum
from dataclasses import dataclass, field
from tkinter import N


class UserSubscription(Enum):
    BASIC = "basic"
    PREMIUM = "premium"
    NOT_SUBSCRIBED = "free"


@dataclass
class User:
    user_id: int
    personal_email: str = field(default=None)
    password: str = field(default=None)
    secret: str = field(default=None)
    email_limit: int = field(default=200)
    audio_limit: int = field(default=20)
    subscription: UserSubscription = field(default=UserSubscription.NOT_SUBSCRIBED) 
    sub_duration: int = field(default=None)