import re

from pydantic import BaseModel, Field, field_validator, model_validator


class _Signup(BaseModel):
    username: str = Field(..., pattern=r"^[a-z0-9_]{3,20}$")
    email: str
    phone: str
    password: str = Field(..., min_length=8)
    password_confirm: str

    @field_validator("email")
    @classmethod
    def _email(cls, v):
        v = v.strip().lower()
        if "@" not in v:
            raise ValueError("invalid email")
        return v

    @field_validator("phone", mode="before")
    @classmethod
    def _phone(cls, v):
        if not isinstance(v, str):
            raise ValueError("phone must be a string")
        v = re.sub(r"[\s.\-()]", "", v)
        if not re.fullmatch(r"\+\d{8,15}", v):
            raise ValueError("invalid phone")
        return v

    @model_validator(mode="after")
    def _match(self):
        if self.password != self.password_confirm:
            raise ValueError("passwords do not match")
        return self


def validate_signup(data):
    f = _Signup.model_validate(data)
    return {"username": f.username, "email": f.email, "phone": f.phone}
