"""Domain models for the COSMOS backend.

These are lightweight Pydantic models describing persisted rows. They help
codify shapes used by repository/service layers without coupling to the
request/response schemas in `app/schemas`.
"""

from app.models.enums import Character, Language, StudyStatus


__all__ = ["Character", "Language", "StudyStatus"]
