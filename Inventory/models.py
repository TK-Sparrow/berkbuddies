from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flask_login import UserMixin
from inventory import db,login_manager
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model,UserMixin):
	id = db.Column(db.Integer,primary_key=True)
	username = db.Column(db.String(30), unique=True, nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	password = db.Column(db.String(60), nullable=False)
	mobile_number = db.Column(db.String(60),unique=True,default=None)
	account_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	plan = db.Column(db.Integer,nullable=False,default=0)
	category_count = db.Column(db.Integer,default=5)
	product_count = db.Column(db.Integer,default=25)
	products = db.relationship('Product', backref='product',cascade="all,delete,delete-orphan", lazy=True)
	Images = db.relationship('ProductImage', backref='img',cascade="all,delete,delete-orphan", lazy=True)
	organization_id = db.relationship('OrganizationDetails', backref='org',cascade="all,delete,delete-orphan", lazy=True)
	folders = db.relationship('Folder', backref='folder',cascade="all,delete,delete-orphan", lazy=True)
	comment_id = db.relationship('Comments', backref='ucomment',cascade="all,delete,delete-orphan", lazy=True)
	feedback_id = db.relationship('Feedback', backref='ufeedback',cascade="all,delete,delete-orphan", lazy=True)
	like_id = db.relationship('Likes', backref='ulikes',cascade="all,delete,delete-orphan", lazy=True)

	def __repr__(self):
		return f"User('{self.username}', '{self.email}')"


class Product(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	productname = db.Column(db.String(100),nullable=False)
	descrption = db.Column(db.TEXT,nullable=False)
	url = db.Column(db.String(250),default=None)
	cost = db.Column(db.Float,default=0)
	spl_cost = db.Column(db.Float,default=0)
	date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	date_edited = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	quantity = db.Column(db.Integer,default=0)
	category = db.Column(db.String(100),nullable=False)
	visit = db.Column(db.Integer,nullable=False,default=0)
	visible = db.Column(db.Integer,nullable=False,default=0)
	like = db.Column(db.Integer,nullable=False,default=0)
	product_images = db.relationship('ProductImage', backref='image',cascade="all,delete,delete-orphan", lazy=True)
	comment_id = db.relationship('Comments', backref='comment',cascade="all,delete,delete-orphan", lazy=True)
	like_id = db.relationship('Likes', backref='like',cascade="all,delete,delete-orphan", lazy=True)
	userid = db.Column(db.Integer, db.ForeignKey('user.id',ondelete='CASCADE'), nullable=False)
	folderid = db.Column(db.Integer, db.ForeignKey('folder.id',ondelete='CASCADE'), nullable=False)

	def __repr__(self):
		return f"Product('{self.id}','{self.productname}', '{self.descrption}')"

	def as_dict(self):
		return {'name': self.productname}


class Folder(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	foldername = db.Column(db.String(50),nullable=False)
	folderunder = db.Column(db.Integer,default=0)
	folderimage = db.Column(db.String(20), nullable=False)
	userid = db.Column(db.Integer, db.ForeignKey('user.id',ondelete='CASCADE'), nullable=False)
	products = db.relationship('Product', backref='productf',cascade="all,delete,delete-orphan", lazy=True)

	def __repr__(self):
		return f"Folder('{self.foldername}', '{self.folderunder}')"


class ProductImage(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	imagename = db.Column(db.String(50),nullable=False)
	order = db.Column(db.Integer,nullable=False)
	postid = db.Column(db.Integer, db.ForeignKey('product.id',ondelete='CASCADE'), nullable=False)
	userid = db.Column(db.Integer, db.ForeignKey('user.id',ondelete='CASCADE'), nullable=False)

	def __repr__(self):
		return f"ProductImage('{self.imagename}', '{self.order}')"


class OrganizationDetails(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	name = db.Column(db.String(30), unique=True, nullable=False)
	category = db.Column(db.String(100),nullable=False)
	address = db.Column(db.String(20),  nullable=False)
	city = db.Column(db.String(20), nullable=False)
	state = db.Column(db.String(20),  nullable=False)
	country = db.Column(db.String(20),  nullable=False)
	pincode = db.Column(db.String(20),  nullable=False)
	about = db.Column(db.TEXT, nullable=False)
	slogan = db.Column(db.String(20), nullable=False)
	logo = db.Column(db.String(20), nullable=False)
	color_code1 = db.Column(db.String(20), nullable=False)
	color_code2 = db.Column(db.String(20), nullable=False)
	insta = db.Column(db.String(50),default=None)
	facebook = db.Column(db.String(50),default=None)
	theme_id = db.Column(db.Integer,nullable=False,default=0)
	visit = db.Column(db.Integer,nullable=False,default=0)
	visible = db.Column(db.Integer,nullable=False,default=0)
	account_created = db.Column(db.DateTime, default=datetime.utcnow)
	link_name = db.Column(db.String(30), unique=True, nullable=False)
	userid = db.Column(db.Integer, db.ForeignKey('user.id',ondelete='CASCADE'), nullable=False)

	def __repr__(self):
		return f"OrganizationDetails('{self.name}', '{self.about}','{self.slogan}', '{self.slogan}', '{self.link_name}')"

	def as_dict(self):
		return {'name': self.name}

class Feedback(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	org_id = db.Column(db.Integer,nullable=False,default=0)
	date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id',ondelete='CASCADE'), nullable=False)
	feedback = db.Column(db.TEXT, nullable=False)
	seen = db.Column(db.Integer,nullable=False,default=0)

	def __repr__(self):
		return f"Feedback('{self.org_id}', '{self.feedback}')"

class Comments(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	comment_id = db.Column(db.Integer,default=0)
	org_id = db.Column(db.Integer,nullable=False,default=0)
	date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	post_id = db.Column(db.Integer, db.ForeignKey('product.id',ondelete='CASCADE'), nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id',ondelete='CASCADE'), nullable=False)
	comments = db.Column(db.TEXT, nullable=False)
	seen = db.Column(db.Integer,nullable=False,default=0)
	
	def __repr__(self):
		return f"Comments('{self.post_id}', '{self.comments}')"



class Likes(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	org_id = db.Column(db.Integer,nullable=False,default=0)
	post_id = db.Column(db.Integer, db.ForeignKey('product.id',ondelete='CASCADE'), nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id',ondelete='CASCADE'), nullable=False)
	date_liked = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

	def __repr__(self):
		return f"Comments('{self.post_id}', '{self.user_id}')"

class Berk_Feedback(db.Model):
	id = db.Column(db.Integer,primary_key=True)
	username = db.Column(db.String(30),  nullable=False)
	email = db.Column(db.String(120),  nullable=False)
	date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)	
	feedback = db.Column(db.TEXT, nullable=False)
	seen = db.Column(db.Integer,nullable=False,default=0)

	def __repr__(self):
		return f"Feedback('{self.org_id}', '{self.feedback}')"
