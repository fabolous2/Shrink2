from enum import Enum
from datetime import time
from dataclasses import dataclass, field


@dataclass
class EmailSettings:
    user_id: int
    email_subject: str = field(default=None)
    email_text: str = field(default=None)
    quantity: int = field(default=None)
    schedule_time: time = field(default=None)