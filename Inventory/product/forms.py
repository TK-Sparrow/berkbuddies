from flask import session
from flask_wtf import FlaskForm
from wtforms import (StringField,SubmitField,TextAreaField,SelectField,IntegerField,DecimalField,
					MultipleFileField,HiddenField)
from wtforms.validators import DataRequired,Length,ValidationError,EqualTo,URL
from inventory.models import Folder,Product,ProductImage
from flask_login import current_user
from flask_wtf.file import FileField, FileAllowed


class ProductForm(FlaskForm):
	productname = StringField('Product Name',validators=[DataRequired()])
	folderunder = StringField('Category Under')
	descrption = TextAreaField('descrption about product',validators=[DataRequired(),Length(min=25,max=1000)])
	category = SelectField('Product category',
                          choices=[('Clothing & Accessories', 'Clothing & Accessories'), ('Electronics', 'Electronics'),
                                   ('Arts & Entertainment', 'Arts & Entertainment'), ('Animals & Pet Supplies', 'Animals & Pet Supplies'), 
                                   ('Food & Beverages', 'Food & Beverages'), ('Software', 'Software'), 
                                   ('Vehicles & Parts', 'Vehicles & Parts')])
	url = StringField('Url for more info:')
	count = IntegerField('Product Quantity')
	cost = DecimalField('Price of the product')
	offer = DecimalField('Offer %')
	submit = SubmitField('Create')
	update = SubmitField('Update')
	publish = SubmitField("Publish") 
	unpublish = SubmitField("Unpublish")

	def validate_productname(self,productname):
		product = Product.query.filter_by(product=current_user,productname=productname.data).first()
		if product and not ('product_id' in session and session['product_id']==product.id):
			raise ValidationError('The Product Name is already created')

	
class CreateFolderForm(FlaskForm):
	foldername = StringField('Category Name',validators=[DataRequired(),Length(min=3)])
	folderunder = StringField('Category Under')
	submit = SubmitField('Create')
	update = SubmitField('Update')

	def validate_foldername(self,foldername):
		folder = Folder.query.filter_by(folder=current_user,foldername=foldername.data).first()
		if folder and not ('folder_id' in session and session['folder_id']==folder.id):
			raise ValidationError('The Category Name is already created')


class  ImageForm(FlaskForm):
	file = MultipleFileField('Select Picture to upload', validators=[FileAllowed(['jpg', 'png'])])
	submit = SubmitField('Post')

	def validate_submit(self,submit):
		i=0
		if session['product_id']:
			product_id = session['product_id']
			cr_product = Product.query.get_or_404(product_id)
			product_images = ProductImage.query.filter_by(image=cr_product).all()
			if product_images:
				i=len(product_images)
		if self.file.data:
			if (i+len(self.file.data)-1)>10:
				raise ValidationError('Only 10 images is allowed for a product')


class ImageReorder(FlaskForm):
	order = HiddenField("order")
	submit = SubmitField("Save")
	add = SubmitField("Add Image")
		