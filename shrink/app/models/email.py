from dataclasses import dataclass, field


@dataclass
class UserEmail:
    user_id: int
    email_address: str
    email_id: int = field(default=0)

