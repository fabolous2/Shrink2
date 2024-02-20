from dataclasses import dataclass, field


@dataclass
class UserEmail:
    to: str
    email_subject: str
    email_text: str
    user_id: int
    email_limit: int = field(default=50)

    def __str__(self) -> str:
        return self.email_text
