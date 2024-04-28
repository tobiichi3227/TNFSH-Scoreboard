"""
Session Service

Store user connection session and some info like student_id, name
If the connection session has exceeded 30 minutes, this session will be deleted.
"""

from dataclasses import dataclass


@dataclass
class Session:
    session_id: str
    student_id: int
    student_name: str


Session.Empty_Session = Session("", 0, "")
