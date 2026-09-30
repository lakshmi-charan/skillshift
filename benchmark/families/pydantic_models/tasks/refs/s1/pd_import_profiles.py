from typing import Optional

from pydantic import BaseModel, ValidationError, field_validator


class _Row(BaseModel):
    user_id: int
    display_name: str
    bio: Optional[str] = None
    zip_code: str

    @field_validator("display_name")
    @classmethod
    def _name(cls, v):
        v = " ".join(v.split())
        if not v:
            raise ValueError("blank")
        return v

    @field_validator("zip_code", mode="before")
    @classmethod
    def _zip(cls, v):
        return str(v) if isinstance(v, int) and not isinstance(v, bool) else v


def import_profiles(rows):
    out = []
    for row in rows:
        try:
            out.append(_Row.model_validate(row).model_dump())
        except ValidationError:
            continue
    return out
