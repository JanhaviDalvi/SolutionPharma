from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

class RegistrationForm(FlaskForm):

	# to set the db object passed from app.py as instance variable so we can access db here
	def __init__(self, db):
		super().__init__()
		self.db = db

	username = StringField('Username', validators=[DataRequired(), Length(min=2, max=18)])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField("Password", validators=[DataRequired(), Length(min=4, max=18)])
	confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Sign Up')
	
	# using db object received to check if username given in registration form already exits
	def validate_username(self, username):
		user = self.db.user.find_one({'username': username.data})
		if user:
			raise ValidationError("Username already exists! Please choose another username...")

	# to check if email given in registration form already exits
	def validate_email(self, email):
		user = self.db.user.find_one({'email': email.data})
		if user:
			raise ValidationError("Email already exists!")


class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired(), Length(min=2, max=18)])
	password = PasswordField("Password", validators=[DataRequired(), Length(min=4, max=18)])
	remember = BooleanField('Remember Me')
	submit = SubmitField('Login')