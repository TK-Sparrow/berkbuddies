from flask_wtf import FlaskForm
from wtforms import (StringField,PasswordField,SubmitField,IntegerField,HiddenField,SelectField,
					FileField,TextAreaField)
from wtforms.validators import DataRequired,Email,Length,ValidationError,EqualTo
from flask_login import current_user
from inventory.models import User,OrganizationDetails
from flask_wtf.file import FileField, FileAllowed


class RegistrationForm(FlaskForm):
	username = StringField("UserName",validators=[DataRequired(),Length(min=3,max=20)])
	email = StringField("Email",validators=[DataRequired(),Email()])
	password = PasswordField("Password",validators=[DataRequired(),Length(min=8)])
	confirm_pasword = PasswordField("Confirm Pasword",validators=[DataRequired(),EqualTo("password")])
	register = SubmitField("Sign up")

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError('The User Name is already taken.')

class RegisterMail(FlaskForm):	
	email = StringField("Email",validators=[DataRequired(),Email()])
	register = SubmitField("Next")

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError('There is already an account with this email. You must use another email.')

class RequestResetForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')



class LoginForm(FlaskForm):
	email = StringField("Email",validators=[DataRequired(),Email()])
	password = PasswordField("Password",validators=[DataRequired(),Length(min=8)])
	register = SubmitField("Sign In")


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')

class mobile_verification(FlaskForm):
	mobile_number = IntegerField('Enter Mobile Number',validators=[DataRequired()])
	country_code = HiddenField("country code",validators=[DataRequired()])
	submit = SubmitField("Verify")

	def validate_mobile_number(self, mobile_number):
		user = User.query.filter_by(mobile_number=mobile_number.data).first()
		if user and mobile_number.data != current_user.mobile_number:
			raise ValidationError('This Mobile Number is already used')

class OTP_verification(FlaskForm):
	OTP = StringField('Enter OTP',validators=[DataRequired(),Length(min=7,max=7)])
	submit = SubmitField("Verify")

class account_form(FlaskForm):
	username = StringField("UserName",validators=[DataRequired(),Length(min=3,max=20)])
	email = StringField("Email",validators=[DataRequired(),Email()])
	mobile_number = StringField("Mobile Number",validators=[DataRequired()])
	Update = SubmitField("Update")

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user and username.data != current_user.username:
			raise ValidationError('This User Name is already taken')

class organization_form(FlaskForm):
	org_name = StringField("Organization Name",validators=[DataRequired()])
	address = StringField("Address",validators=[DataRequired()])
	city_name = HiddenField("City",validators=[DataRequired()])
	state_name = HiddenField("state",validators=[DataRequired()])
	country_name = HiddenField("country",validators=[DataRequired()])
	pincode = StringField("pincode",validators=[DataRequired()])
	about = TextAreaField("about",validators=[DataRequired(),Length(min=50,max=1000)])
	category = SelectField('Product category',
                          choices=[('Clothing & Accessories', 'Clothing & Accessories'), ('Electronics', 'Electronics'),
                                   ('Arts & Entertainment', 'Arts & Entertainment'), ('Animals & Pet Supplies', 'Animals & Pet Supplies'), 
                                   ('Food & Beverages', 'Food & Beverages'), ('Software', 'Software'), 
                                   ('Vehicles & Parts', 'Vehicles & Parts')])
	slogan = StringField("slogan",validators=[DataRequired()])
	insta = StringField('Instagram link:')
	facebook = StringField('facebook link:')
	background_color1 = HiddenField('Color Code 1')
	background_color2 = HiddenField('Color Code 2')
	logo  = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])
	link_name = StringField("Link Name",validators=[DataRequired(),Length(min=5,max=20)])
	Update = SubmitField("Update") 
	Create = SubmitField("Create") 
	publish = SubmitField("Publish") 
	unpublish = SubmitField("Unpublish") 

	def validate_org_name(self,org_name):
		org = OrganizationDetails.query.filter_by(name=org_name.data).first()
		if org and (org.org!=current_user):
			raise ValidationError('This Organization Name is already taken')



	def validate_link_name(self,link_name):
		org = OrganizationDetails.query.filter_by(link_name=link_name.data).first()
		if org and (org.org!=current_user):
			raise ValidationError('This Link is already taken')

class Reply(FlaskForm):
	comment = StringField('Reply Comment',validators=[DataRequired()])
	submit = SubmitField("Reply")