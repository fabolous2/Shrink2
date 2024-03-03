from enum import Enum
from dataclasses import dataclass, field


class AdminStatus(Enum):
    OWNER = 'Owner'
    HEAD_ADMIN = 'Head Admin'
    MODERATOR = 'Moderator'


@dataclass
class Admin:
    admin_id: int
    username: str
    real_name: str
    admin_status: AdminStatus