from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FileField, IntegerField, RadioField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask_wtf.file import FileField, FileAllowed
from wtforms import ValidationError

from flask_login import current_user
from Tool.models import User


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    name = StringField('First Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo(
        'pass_confirm', message='Passwords must match'), Length(min=8, max=16)])
    pass_confirm = PasswordField(
        'Confirm Password', validators=[DataRequired()])
    picture = FileField(' Profile Picture', validators=[
                        FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(
                'The email you chose has already been registered')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(
                'The username you chose has already been registered')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log in')


class UpdateUserForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    username = StringField('Username', validators=[DataRequired()])
    picture = FileField('Update Profile Picture', validators=[
                        FileAllowed(['jpg', 'png'])])
    submit = SubmitField('Update')

    def validate_email(self, field):
        if field.data != current_user.email:
            if User.query.filter_by(email=field.data).first():
                raise ValidationError(
                    'The email you chose has already been registered')

    def validate_username(self, field):
        if field.data != current_user.username:
            if User.query.filter_by(username=field.data).first():
                raise ValidationError(
                    'The username you chose has already been registered')


class CalculateForm(FlaskForm):
    d1 = IntegerField('No. of polythene bags you get at home',
                      validators=[DataRequired()])
    d2 = IntegerField('No. of bread and milk packets consumed',
                      validators=[DataRequired()])
    d3 = IntegerField('No. of biscuits/chips/maggi packets etc. consumed',
                      validators=[DataRequired()])
    d4 = IntegerField('No. of plastic packets bought in monthly groceries (pulses, rice, wheat, sugar, salt, spices, poha, semolina.)',
                      validators=[DataRequired()])
    d5 = IntegerField('As part of online/takeaway food ordering, no. of plastic containers',
                      validators=[DataRequired()])
    d6 = IntegerField('No. of non reusable plastic bottles used in a week (coke, mineral water, other soft drinks)',
                      validators=[DataRequired()])
    d7 = IntegerField('Styrofoam Cups/Plates as disposable Styrofoam',
                      validators=[DataRequired()])
    submit = SubmitField('Update')
