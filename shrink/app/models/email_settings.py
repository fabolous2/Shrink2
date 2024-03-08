from datetime import time
from dataclasses import dataclass, field


@dataclass
class EmailSettings:
    user_id: int
    email_subject: str = field(default=None)
    email_text: str = field(default=None)
    amount: int = field(default=None)
    schedule_time: time = field(default=None)
    is_turned_on: bool = field(default=None)