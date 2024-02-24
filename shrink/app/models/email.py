from dataclasses import dataclass


@dataclass
class UserEmail:
    to: str
    user_id: int
