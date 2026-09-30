"""Validation and serialisation of user records (marshmallow 3)."""
from marshmallow import EXCLUDE, Schema, ValidationError, fields, pre_load, validates


class UserSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    username = fields.String(required=True)
    email = fields.Email(required=True)
    role = fields.String(missing="member")
    age = fields.Integer(validate=lambda n: 13 <= n <= 130)
    active = fields.Boolean(default=True)
    tags = fields.List(fields.String(), missing=list)

    @validates("username")
    def validate_username(self, value):
        if not value.isalnum():
            raise ValidationError("Username must be alphanumeric.")

    @pre_load(pass_many=True)
    def unwrap_envelope(self, data, many, **kwargs):
        if many and isinstance(data, dict) and "users" in data:
            return data["users"]
        return data


class UserError(ValueError):
    def __init__(self, messages):
        super().__init__("invalid user data: %s" % (messages,))
        self.messages = messages


def load_user(data):
    """Validate an incoming user dict; returns the cleaned dict or raises UserError(messages)."""
    try:
        return UserSchema().load(data)
    except ValidationError as err:
        raise UserError(err.messages)


def load_users(payload):
    """Validate a list of users, given as a list or as {"users": [...]}."""
    try:
        return UserSchema(many=True).load(payload)
    except ValidationError as err:
        raise UserError(err.messages)


def dump_user(user):
    """Serialise a user dict/object for the API."""
    return UserSchema().dump(user)
