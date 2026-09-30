"""Sign-up form validation."""
import re
from typing import Annotated

from pydantic import AfterValidator, BaseModel, Field, model_validator


def _normalise_phone(value: str) -> str:
    """'+' followed by 8-15 digits; spaces, dots, dashes and parentheses in the input are ignored."""
    compact = re.sub(r"[\s.\-()]", "", value)
    if not re.fullmatch(r"\+\d{8,15}", compact):
        raise ValueError("invalid phone number")
    return compact


PhoneNumber = Annotated[str, AfterValidator(_normalise_phone)]


class SignupForm(BaseModel):
    username: str = Field(..., pattern=r"^[a-z0-9_]{3,20}$")
    email: str
    phone: PhoneNumber
    password: str = Field(..., min_length=8)
    password_confirm: str

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.password_confirm:
            raise ValueError("passwords do not match")
        return self


def parse_signup(data):
    """Validate a sign-up payload (dict). Raises pydantic.ValidationError (a ValueError) if invalid."""
    return SignupForm.model_validate(data)
