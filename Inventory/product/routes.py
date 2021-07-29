from flask import render_template,url_for,Blueprint,redirect,flash,request,session,abort,Response,current_app
from flask_login import login_user,current_user,login_required

from inventory.product.forms import ProductForm,CreateFolderForm,ImageForm,ImageReorder
from inventory.users.utility import save_picture,to_s3,delete_img_s3
from inventory import db
from inventory.models import Folder,Product,ProductImage
import secrets
import os

products = Blueprint('products',__name__)


@products.route('/create_product/',methods=['POST','GET'])
@login_required
def create_product():
	pro_count = Product.query.filter_by(product=current_user).all()
	if(len(pro_count)>=current_user.product_count):
		flash('You reached your Product Limit','danger')
		return redirect(url_for('products.dashboard'))
	form = ProductForm()
	if form.validate_on_submit():
		folder = Folder.query.filter_by(folder=current_user,foldername=form.folderunder.data).first()
		product = Product(productname=form.productname.data,descrption=form.descrption.data,
			url=form.url.data,cost=form.cost.data,spl_cost=form.offer.data,quantity=form.count.data,
			category=form.category.data,product=current_user,productf=folder)
		db.session.add(product)
		db.session.commit()
		flash('product created','success')
		return redirect(url_for('products.product_photos',product_id=product.id))
	form.folderunder.data = session['folder']
	return render_template('create_product.html',form=form,title='create product',product_id=0)



@products.route('/update_product/<int:product_id>',methods=['POST','GET'])
@login_required
def update_product(product_id):
	cr_product = Product.query.get_or_404(product_id)
	if cr_product.product != current_user:
		abort(403)
	session['product_id'] = product_id
	visible = 0
	form = ProductForm()
	if form.validate_on_submit():
		if form.unpublish.data:
			cr_product.visible = 1
			db.session.commit()
			flash('This product not visble in your store','success')

		elif form.publish.data:
			cr_product.visible = 0
			db.session.commit()
			flash('This product visble in your store','success')

		else:
			cr_product.productname = form.productname.data
			cr_product.descrption = form.descrption.data
			cr_product.url = form.url.data
			cr_product.cost = form.cost.data
			cr_product.spl_cost = form.offer.data
			cr_product.quantity = form.count.data
			cr_product.category = form.category.data
			db.session.commit()
			flash('product updated','success')
			return redirect(url_for('products.dashboard'))
	elif request.method == 'GET':
		form.folderunder.data = cr_product.productf.foldername
		form.productname.data = cr_product.productname
		form.descrption.data = cr_product.descrption
		form.url.data = cr_product.url
		form.cost.data = cr_product.cost
		form.offer.data = cr_product.spl_cost
		form.count.data = cr_product.quantity
		form.category.data = cr_product.category
		visible = cr_product.visible
	return render_template('create_product.html',form=form,title='update product',
							product_id=cr_product.id,visible=visible)

@products.route('/delete_product/<string:product_id>',methods=['POST'])
@login_required
def delete_product(product_id):
	product_id =int(product_id)
	cr_product = Product.query.get_or_404(product_id)
	if cr_product.product != current_user:
		abort(403)
	db.session.delete(cr_product)
	db.session.commit()
	flash('Your Product has been deleted!', 'success')
	return redirect(url_for('products.dashboard'))


@products.route('/create_folder/',methods=['POST','GET'])
@login_required
def create_folder():
	form = CreateFolderForm()
	current_folder_name = session['folder']
	current_folder_id=0
	current_folder = Folder.query.filter_by(foldername=current_folder_name,folder=current_user).first()
	if current_folder:
		current_folder_id = current_folder.id
	if form.validate_on_submit():
		folder = Folder(foldername=form.foldername.data,folderunder = current_folder_id,folder=current_user,folderimage="")
		db.session.add(folder)
		db.session.commit()
		flash('Folder created','success')
		return redirect(url_for('products.dashboard'))
	form.folderunder.data=current_folder_name
	return render_template('create_folder.html',form=form,title='create Category')

@products.route('/update_folder/',methods=['POST','GET'])
@login_required
def update_folder():
	form = CreateFolderForm()
	current_folder_name = session['folder']
	current_folder = Folder.query.filter_by(foldername=current_folder_name,folder=current_user).first()
	if current_folder==None:
		flash('Invalid Request','danger')
		return redirect(url_for('products.dashboard'))
	session['folder_id'] = current_folder.id
	if form.validate_on_submit():
		current_folder.foldername=form.foldername.data
		db.session.commit()
		flash('Folder Name Updated','success')
		return redirect(url_for('products.dashboard'))
	elif request.method == 'GET':
		form.foldername.data = current_folder.foldername
		if current_folder.folderunder==0:
			form.folderunder.data = 'main'
		else:
			folder = Folder.query.get(current_folder.folderunder)
			form.folderunder.data = folder.foldername
	return render_template('create_folder.html',form=form,title='update Category')




@products.route('/delete_folder/',methods=['POST','GET'])
@login_required
def delete_folder():
	current_folder_name = session['folder']
	current_folder = Folder.query.filter_by(foldername=current_folder_name,folder=current_user).first()
	if current_folder==None:
		flash('Invalid Request','danger')
		return redirect(url_for('products.dashboard'))
	cr_folders = Folder.query.filter_by(folderunder=current_folder.id,folder=current_user)
	for cr_folder in cr_folders:
		db.session.delete(cr_folder)
		db.session.commit()
	db.session.delete(current_folder)
	db.session.commit()
	flash('Your Category has been deleted!', 'success')
	session.pop('folder',None)
	return redirect(url_for('products.dashboard'))

@products.route('/delete_all_folder/',methods=['POST','GET'])
@login_required
def delete_all_folder():
	current_folder = Folder.query.filter_by(folder=current_user).all()
	if current_folder==None:
		flash('Invalid Request','danger')
		return redirect(url_for('products.dashboard'))
	for cr_folder in current_folder:
		folder = Folder.query.filter_by(foldername=cr_folder.foldername,folder=current_user).first()
		db.session.delete(cr_folder)
		db.session.commit()
	flash('All Category has been deleted!', 'success')
	session.pop('folder',None)
	return redirect(url_for('products.dashboard'))



@products.route('/products/',methods=['POST','GET'])
@login_required
def dashboard():
	img_list={}
	session.pop('folder_id',None)
	current_folder_name='main'
	current_folder_id = 0
	session.pop('product_id',None)
	if 'folder' in session and session['folder']!='main':
		current_folder_name = session['folder']
		current_folder = Folder.query.filter_by(foldername=current_folder_name,folder=current_user).first()
		if current_folder==None:
			session.pop('folder',None)
			if(foldername != 'main'):
				flash('invalid folder name','danger')
			return redirect(url_for('products.dashboard'))

		current_folder_id = current_folder.id
	else:
		current_folder_name = 'main'
		current_folder_id = 0
		session['folder'] = 'main'
		session['lastfolder']=[]
	folderr = Folder.query.filter_by(folder=current_user,foldername=current_folder_name).first()
	folders = Folder.query.filter_by(folder=current_user,folderunder=current_folder_id).all()
	products = Product.query.filter_by(product=current_user,productf=folderr).all()
	for product in products:
		img = ProductImage.query.filter_by(image=product).order_by(ProductImage.order).first()
		if img:
			img_list[product.id] = img.imagename
	return render_template('dashboard.html',title='Product',folders=folders,
		lastfolder=session['lastfolder'],products=products,img_list=img_list)


@products.route('/dashboard/<string:foldername>')
@login_required
def changefolder(foldername):
	folders = Folder.query.filter_by(folder=current_user,foldername=foldername).all()
	if foldername == 'main' or folders==[]:
		session.pop('folder',None)
		if(folders==[] and foldername != 'main'):
			flash('invalid folder name','danger')
		return redirect(url_for('products.dashboard'))
	lastfolder = session['lastfolder']
	if foldername in lastfolder:
		lastfolder = lastfolder[0:lastfolder.index(foldername)]
	else:
		lastfolder.append(session['folder'])
	session['lastfolder']=lastfolder
	session['folder'] = foldername
	return redirect(url_for('products.dashboard'))



@products.route('/product_photos/<int:product_id>',methods=['POST','GET'])
@login_required
def product_photos(product_id):
	cr_product = Product.query.get_or_404(product_id)
	if cr_product.product != current_user:
		abort(403)
	session['product_id'] = product_id
	form = ImageForm()
	t=10
	product_imagess = ProductImage.query.filter_by(image=cr_product).all()
	if product_imagess:
		t = t-len(product_imagess)
	if form.validate_on_submit():
		i=1
		product_images = ProductImage.query.filter_by(image=cr_product).order_by(ProductImage.order.desc()).first()
		if product_images:
			i=i+product_images.order
		if form.file.data:
			uploaded_files = request.files.getlist("file")
			for images in uploaded_files:
				picture_file = to_s3(images)
				print(images)
				productimage = ProductImage(imagename=picture_file,image=cr_product,order=i,img=current_user)
				db.session.add(productimage)
				i=i+1
				print(i)
				db.session.commit()

			# for images in form.file.data:
			# 	if type(images) != str:
			# 		images_filename=save_picture(images)
			# 		productimage = ProductImage(imagename=images_filename,image=cr_product,order=i,img=current_user )
			# 		db.session.add(productimage)
			# 		i=i+1
			# db.session.commit()
		return redirect(url_for('products.dashboard'))
	flash('Only '+str(t)+' Images is allowed','info')	
	return render_template('drag.html',form=form,title="Product Image",t=t)

@products.route('/change_product_photos/<int:product_id>',methods=['POST','GET'])
@login_required
def change_product_photos(product_id):
	cr_product = Product.query.get_or_404(product_id)
	if cr_product.product != current_user:
		abort(403)
	form = ImageReorder()
	if form.validate_on_submit():
		if form.add.data:
			return redirect(url_for('products.product_photos',product_id=product_id))
		else:
			reorder = form.order.data[:-1].split(',')
			i=1
			for o in reorder:
				img = ProductImage.query.get(int(o))
				img.order = i
				db.session.commit()
				i=i+1
		flash('product updated','success')
		return redirect(url_for('products.dashboard'))
	product_images = ProductImage.query.filter_by(image=cr_product).order_by(ProductImage.order).all()
	return render_template('edit_post_image.html',product_images=product_images,form=form,title='Product')


@products.route('/delete_product_image/<int:img_id>')
@login_required
def delete_image(img_id):
	img = ProductImage.query.get(img_id)
	product_id=img.image.id
	img_name = img.imagename
	db.session.delete(img)
	db.session.commit()
	delete_img_s3("product_posts/"+img_name)
	#os.remove (file_path)
	flash('Image has been delete has been deleted!', 'success')
	return redirect(url_for('products.change_product_photos',product_id=product_id))
