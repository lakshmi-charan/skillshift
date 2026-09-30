"""Sign-up form validation (written against pydantic 1.10)."""
import re

from pydantic import BaseModel, Field, root_validator


class PhoneNumber(str):
    """Phone number in international form: '+' followed by 8-15 digits.
    Spaces, dots, dashes and parentheses in the input are ignored."""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, value):
        if not isinstance(value, str):
            raise TypeError("phone number must be a string")
        compact = re.sub(r"[\s.\-()]", "", value)
        if not re.fullmatch(r"\+\d{8,15}", compact):
            raise ValueError("invalid phone number")
        return cls(compact)


class SignupForm(BaseModel):
    username: str = Field(..., regex=r"^[a-z0-9_]{3,20}$")
    email: str
    phone: PhoneNumber
    password: str = Field(..., min_length=8)
    password_confirm: str

    @root_validator
    def passwords_match(cls, values):
        password, confirm = values.get("password"), values.get("password_confirm")
        if password is not None and confirm is not None and password != confirm:
            raise ValueError("passwords do not match")
        return values


def parse_signup(data):
    """Validate a sign-up payload (dict). Raises pydantic.ValidationError (a ValueError) if invalid."""
    return SignupForm.parse_obj(data)
