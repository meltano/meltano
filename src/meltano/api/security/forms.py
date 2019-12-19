from flask import url_for
from flask_security.forms import LoginForm, RegisterForm, ConfirmRegisterForm
from flask_security.utils import _datastore, get_message
from wtforms import StringField
from wtforms.validators import Required, ValidationError, Length


username_required = Required(message="USERNAME_NOT_PROVIDED")
username_validator = Length(min=6, max=32, message="USERNAME_INVALID")


def unique_username(form, field):
    if _datastore.get_user(field.data) is not None:
        msg = get_message("USERNAME_ALREADY_TAKEN", username=field.data)[0]
        raise ValidationError(msg)


class MeltanoLoginForm(LoginForm):
    email = StringField("Username or Email Address", validators=[Required()])

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.next.data = self.next.data or url_for("root.bootstrap")


class UniqueUsernameMixin:
    username = StringField(
        "Username", validators=[username_required, username_validator, unique_username]
    )


class MeltanoConfirmRegisterForm(ConfirmRegisterForm, UniqueUsernameMixin):
    pass


class MeltanoRegisterFrom(RegisterForm, UniqueUsernameMixin):
    pass
