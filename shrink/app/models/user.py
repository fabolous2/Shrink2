from enum import Enum
from datetime import time
from dataclasses import dataclass, field


class UserSubscription(Enum):
    BASIC = "basic"
    PREMIUM = "premium"
    NOT_SUBSCRIBED = "not_subscribed"


@dataclass
class User:
    user_id: int
    password: str = field(default=None)
    quantity: int = field(default=None)
    personal_email: str = field(default=None)
    schedule_time: time = field(default=None)
    subscription: UserSubscription = field(default=UserSubscription.NOT_SUBSCRIBED)
