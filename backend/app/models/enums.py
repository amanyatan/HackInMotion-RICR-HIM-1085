"""Shared Pydantic value models.

These are pure data shapes (mostly enums/constants validation). They are kept
separate from request/response schemas in `app/schemas`.
"""

from enum import Enum


class Character(str, Enum):
    KEI = "kei"
    MARK = "mark"


class Language(str, Enum):
    EN = "en"
    JA = "ja"
    KO = "ko"
    ZH = "zh"


class StudyStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    PAUSED = "paused"
    COMPLETED = "completed"
