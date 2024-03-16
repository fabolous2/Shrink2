from dataclasses import dataclass


@dataclass
class UserAudio:
    id: int
    file_id: str
    name: str
    size: int
    user_id: int
    audio_index: int
