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
    expire_time: float
    student_id: int
    student_name: str


class SessionService:
    EmptySession = Session("", 0, 0, "")

    def __init__(self) -> None:
        SessionService.inst: "SessionService" = self
        self.sessions: dict[str, Session] = {}

    def is_session_expire(self, session_id: str) -> ReturnType:
        if session_id not in self.sessions:
            return NotExistError, None

        if self.sessions[session_id].expire_time - time.time() > ThirtyMinute:
            return Success, True

        return Success, False

    def create_session(self, session_id: str, student_id: int, name: str) -> ReturnType:
        if session_id in self.sessions:
            return ExistError, None

        self.sessions[session_id] = Session(session_id, time.time(), student_id, name)
        return Success, None

    def remove_session(self, session_id: str) -> ReturnType:
        if session_id not in self.sessions:
            return NotExistError, None

        self.sessions.pop(session_id)
        return Success, None

    def get_session(self, session_id: str) -> ReturnType:
        if session_id not in self.sessions:
            return NotExistError, None

        return Success, self.sessions[session_id]
