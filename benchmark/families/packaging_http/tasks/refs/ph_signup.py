from marshmallow import EXCLUDE, Schema, ValidationError, fields, validate


class _Signup(Schema):
    class Meta:
        unknown = EXCLUDE

    username = fields.String(required=True, validate=validate.Regexp(r"^[A-Za-z0-9]+$"))
    email = fields.Email(required=True)
    plan = fields.String(load_default="free", validate=validate.OneOf(["free", "pro", "team"]))
    age = fields.Integer(validate=validate.Range(min=16, max=120))


class SignupError(ValueError):
    def __init__(self, messages):
        super().__init__(str(messages))
        self.messages = messages


def validate_signup(data):
    try:
        return _Signup().load(data)
    except ValidationError as err:
        raise SignupError(err.messages)
