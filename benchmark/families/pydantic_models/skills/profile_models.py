"""User profile records exchanged with the account service (written against pydantic 1.10)."""
from typing import List, Optional

from pydantic import BaseModel, validator


class Profile(BaseModel):
    user_id: int
    display_name: str
    bio: Optional[str]
    website: Optional[str] = None
    zip_code: str
    tags: List[str] = []

    @validator("display_name")
    def clean_display_name(cls, value):
        value = " ".join(value.split())
        if not value:
            raise ValueError("display_name must not be blank")
        return value


def load_profile(data):
    """Validate a profile payload (dict) and return a Profile. Raises ValidationError if invalid."""
    return Profile.parse_obj(data)


def public_view(profile):
    """Dict for the public API: everything except user_id, leaving out fields that are None."""
    return profile.dict(exclude={"user_id"}, exclude_none=True)


def apply_changes(profile, changes):
    """Return a copy of `profile` with the given field values replaced; the original is unchanged."""
    return profile.copy(update=changes)
