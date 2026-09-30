from typing import Optional

from pydantic import BaseModel, ValidationError, validator


class _Row(BaseModel):
    user_id: int
    display_name: str
    bio: Optional[str]
    zip_code: str

    @validator("display_name")
    def _name(cls, v):
        v = " ".join(v.split())
        if not v:
            raise ValueError("blank")
        return v


def import_profiles(rows):
    out = []
    for row in rows:
        try:
            out.append(_Row.parse_obj(row).dict())
        except ValidationError:
            continue
    return out
