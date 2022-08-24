from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    SubmitField,
    BooleanField,
    SelectField,
    TextAreaField,
    HiddenField,
)
from wtforms.validators import DataRequired, EqualTo, Email, Optional, Length

MIN_PWD_LENGTH = 5;


""" Create a PasswordField. """
def gen_pwd_field():
    return PasswordField('Password', validators=[DataRequired(), Length(min=MIN_PWD_LENGTH)])


class RegistrationForm(FlaskForm):
    email = StringField('Amherst Student Email', validators=[DataRequired(), Email()])
    password = gen_pwd_field()
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password')]
    )
    submit = SubmitField('Sign Up!')


class LoginForm(FlaskForm):                                                                    
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

GRADES = [
    'A+',
    'A',
    'A-',
    'B+',
    'B',
    'B-',
    'C+',
    'C',
    'C-',
    'D+',
    'D',
    'D-',
    'F',
]

class ReviewForm(FlaskForm):                                                                    
    department = SelectField('Department', choices=[""], validators=[DataRequired()])
    course = SelectField('Course', choices=[""], validators=[DataRequired()])
    term = SelectField('Term', choices=[""], validators=[DataRequired()])
    section = SelectField('Section', choices=[""], validators=[DataRequired()])

    professor_rating = HiddenField('Professor Rating', default=1)
    difficulty_rating = HiddenField('Difficulty Rating', default=1)
    workload_rating = HiddenField('Workload Rating', default=1)
    interesting_rating = HiddenField('Interesting Rating', default=1)
    grade = SelectField('Grade', choices=GRADES, default='')
    text = TextAreaField('Comments (Optional)', [Optional(), Length(max=500)])

    submit = SubmitField('Submit')


class ResetRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Reset')


class ResetForm(FlaskForm):
    password = gen_pwd_field()
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password')]
    )
    submit = SubmitField('Reset Password')
