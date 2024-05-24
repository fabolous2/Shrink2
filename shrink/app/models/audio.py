from dataclasses import dataclass, field


@dataclass
class UserAudio:
    id: int
    file_id: str
    name: str
    size: int
    user_id: int
    audio_index: int
    is_extra: int = field(default = 0)
    available_is_for_audio: int = field(default=1)
