from dataclasses import dataclass


@dataclass
class UserAudio:
    file_id: int
    name: str
    size: int
    user_id: int
