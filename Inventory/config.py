import os
from os import environ
from dotenv import load_dotenv
APP_ROOT = os.path.join(os.path.dirname(__file__), '..')   # refers to application_top
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)


class Config:
	SECRET_KEY = os.getenv('SECRET_KEY')
	basedir = os.path.abspath(os.path.dirname(__file__))
	#SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
	SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	VERIFICATION_SID = os.getenv('VERIFICATION_SID')
	TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
	TWILIO_AUTH_TOKEN  = os.getenv('TWILIO_AUTH_TOKEN')
	SESSION_COOKIE_SAMESITE = None
	AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
	AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
	BUCKET = os.getenv('BUCKET')
	MAX_CONTENT_LENGTH  = 1 * 1024 * 1024