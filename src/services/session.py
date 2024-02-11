"""
Session Service

Store user connection session and some info like student_id, name
If the connection session has exceeded 30 minutes, this session will be deleted.
"""

import time
from dataclasses import dataclass

from utils.error import ReturnType
from utils.error import Success, NotExistError, ExistError

ThirtyMinute: float = 30 * 60


@dataclass
class Session:
    session_id: str
    student_id: int
    student_name: str
    # expire_time: float


Session.Empty_Session = Session("", 0, "")
