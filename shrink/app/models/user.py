from datetime import time
from dataclasses import dataclass, field


@dataclass
class User:
    user_id: int
    personal_email: str = field(default=None)
    password: str = field(default=None)
    premium: bool = field(default=None)
    schedule_time: time = field(default=None)
    quantity: int = field(default=None)
