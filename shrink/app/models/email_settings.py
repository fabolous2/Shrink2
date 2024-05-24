from datetime import time
from dataclasses import dataclass, field
from enum import Enum


class FrequencyStatus(Enum):
    one_day_a_week = 1
    two_day_a_week = 2
    three_day_a_week = 3
    four_day_a_week = 4

@dataclass
class EmailSettings:
    user_id: int
    email_subject: str = field(default=None)
    email_text: str = field(default=None)
    amount: int = field(default=2)
    schedule_time: time = field(default=None)
    frequency: int = field(default=1)
    current_frequency: int = field(default=1)
    is_turned_on: bool = field(default=None)
    email_limit_to_send: int = field(default=25)
    email_limit_to_send_for_extra: int = field(default=0)
    advice_for_frequency: int = field(default=0)
    advice_for_quantity: int = field(default=0)