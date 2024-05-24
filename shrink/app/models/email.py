from dataclasses import dataclass, field


@dataclass
class UserEmail:
    id: int
    user_id: int
    email_address: str
    email_id: int = field(default=0)
    last_sent_index: int = field(default=0)
    available_is: int = field(default=1)
