from dataclasses import dataclass

@dataclass
class SentAudio:
    sent_audio_id: int
    email_id: int
    audio_id: int
    send_date: int