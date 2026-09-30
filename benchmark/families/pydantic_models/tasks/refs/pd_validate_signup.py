import re

from pydantic import BaseModel, Field, root_validator, validator


class _Signup(BaseModel):
    username: str = Field(..., regex=r"^[a-z0-9_]{3,20}$")
    email: str
    phone: str
    password: str = Field(..., min_length=8)
    password_confirm: str

    @validator("email")
    def _email(cls, v):
        v = v.strip().lower()
        if "@" not in v:
            raise ValueError("invalid email")
        return v

    @validator("phone", pre=True)
    def _phone(cls, v):
        if not isinstance(v, str):
            raise ValueError("phone must be a string")
        v = re.sub(r"[\s.\-()]", "", v)
        if not re.fullmatch(r"\+\d{8,15}", v):
            raise ValueError("invalid phone")
        return v

    @root_validator(skip_on_failure=True)
    def _match(cls, values):
        if values["password"] != values["password_confirm"]:
            raise ValueError("passwords do not match")
        return values


def validate_signup(data):
    f = _Signup.parse_obj(data)
    return {"username": f.username, "email": f.email, "phone": f.phone}
