from enum import Enum
from dataclasses import dataclass, field


class UserSubscription(Enum):
    BASIC = "basic"
    PREMIUM = "premium"
    NOT_SUBSCRIBED = "not_subscribed"


@dataclass
class User:
    user_id: int
    personal_email: str = field(default=None)
    password: str = field(default=None)
    email_limit: int = field(default=50)
    subscription: UserSubscription = field(default=UserSubscription.NOT_SUBSCRIBED)