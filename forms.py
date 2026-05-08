from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.fields import EmailField
from wtforms.validators import DataRequired, Email, EqualTo, Length


# ── REGISTER FORM ──
class RegisterForm(FlaskForm):
    name = StringField(
        'name',
        validators=[
            DataRequired(message='Name is required.'),
            Length(min=2, max=100, message='Name must be between 2 and 100 characters.')
        ]
    )
    email = EmailField(
        'e-mail',
        validators=[
            DataRequired(message='Email is required.'),
            Email(message='Please enter a valid email address.')
        ]
    )
    password = PasswordField(
        'password',
        validators=[
            DataRequired(message='Password is required.'),
            Length(min=6, message='Password must be at least 6 characters.')
        ]
    )
    repeat_password = PasswordField(
        'repeat password',
        validators=[
            DataRequired(message='Please repeat your password.'),
            EqualTo('password', message='Passwords must match.')
        ]
    )
    invite_code = StringField(
        'invite code',
        validators=[
            DataRequired(message='Invite code is required.')
        ]
    )
    submit = SubmitField('Join Now')


# ── LOGIN FORM ──
class LoginForm(FlaskForm):
    email = EmailField(
        'e-mail',
        validators=[
            DataRequired(message='Email is required.'),
            Email(message='Please enter a valid email address.')
        ]
    )
    password = PasswordField(
        'password',
        validators=[
            DataRequired(message='Password is required.')
        ]
    )
    submit = SubmitField('Log In')
