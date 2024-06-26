from flask import current_app
from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    PasswordField,
    StringField,
    SubmitField,
    ValidationError,
)
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp

from ..models import User


class LoginForm(FlaskForm):
    """User's login form."""

    email = StringField(
        "Email", validators=[DataRequired(), Length(1, 64), Email()]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Keep me logged in")
    submit = SubmitField("Log in")


class RegistrationForm(FlaskForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with current_app.app_context():
            self.passwd_min_len = current_app.config["PASSWORD_MIN_LENGTH"]

    email = StringField(
        "Email", validators=[DataRequired(), Length(1, 64), Email()]
    )
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(1, 64),
            Regexp(
                "^[A-Za-z0-9][A-Za-z0-9_.]*$",
                0,
                "Usernames must have only letters, numbers, dots or "
                "underscores",
            ),
        ],
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            EqualTo("password2", message="Passwords must match."),
        ],
    )
    password2 = PasswordField("Confirm password", validators=[DataRequired()])
    submit = SubmitField("Register")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError("Email already registered.")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError("Username already in use.")

    def validate_password(self, field):
        if len(field.data) < self.passwd_min_len:
            raise ValidationError(
                f"Password minimum length should be at least {self.passwd_min_len} characters"
            )


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField("Old password", validators=[DataRequired()])
    password = PasswordField(
        "New password",
        validators=[
            DataRequired(),
            EqualTo("password2", message="Passwords must match."),
        ],
    )
    password2 = PasswordField(
        "Confirm new password", validators=[DataRequired()]
    )
    submit = SubmitField("Update Password")


class PasswordResetRequestForm(FlaskForm):
    email = StringField(
        "Email", validators=[DataRequired(), Length(1, 64), Email()]
    )
    submit = SubmitField("Reset Password")


class PasswordResetForm(FlaskForm):
    password = PasswordField(
        "New Password",
        validators=[
            DataRequired(),
            EqualTo("password2", message="Passwords must match"),
        ],
    )
    password2 = PasswordField("Confirm password", validators=[DataRequired()])
    submit = SubmitField("Reset Password")


class ChangeEmailForm(FlaskForm):
    email = StringField(
        "New Email", validators=[DataRequired(), Length(1, 64), Email()]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Update Email Address")

    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError("Email already registered.")
