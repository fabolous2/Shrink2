from dataclasses import dataclass, field


@dataclass
class UserAudio:
    file_id: int
    name: str
    size: int
    user_id: int
    is_sent: bool = field(default=False)
