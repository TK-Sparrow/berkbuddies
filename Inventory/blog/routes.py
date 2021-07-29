from flask import (render_template,url_for,Blueprint,redirect,flash,request,session,abort,
				current_app,json,jsonify)
from inventory.models import (User,OrganizationDetails,Folder,Product,ProductImage,
							Feedback,Comments,Likes,Berk_Feedback)
from inventory.blog.forms import ShopSearch,feedback,Reply,EdmundsForm,ProductSearch
from flask_login import current_user,login_required
from sqlalchemy import or_
from inventory import db
from urllib.request import urlopen

from logging import FileHandler, WARNING

# logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.DEBUG)

# formatter = logging.Formatter('%(levelname)s:%(name)s:%(message)s')

file_handler = FileHandler('employee.log')
file_handler.setLevel(WARNING)
# file_handler.setFormatter(formatter)

#logger.addHandler(file_handler)

blog = Blueprint('blog',__name__)
#blog.logger.addHandler(file_handler)

@blog.route('/',methods=['POST','GET'])
def berkbuddy_home():
	return render_template('index.html',title="Home")


@blog.route('/testerror',methods=['POST','GET'])
def berkbuddy_testerror():
	print(kiol)
	return render_template('index.html',title="Home")

@blog.route('/errorlog_shit') 
def errorlog_shit(): 
	with open('errorlog_shit.txt', 'r') as f: 
		return render_template('errorlog_shit.html', text=f.read())

@blog.route('/hell_list') 
def user_list(): 
	users = User.query.all()
	u=[]
	for user in users:
		u.append(user.username)
	return render_template('user_list.html',ulist = u,ulen = len(u))

@blog.route('/about',methods=['POST','GET'])
def berkbuddy_about():
	return render_template('berk_about.html',title="About")

@blog.route('/contact',methods=['POST','GET'])
def berkbuddy_contact():
	return render_template('berk_contact.html',title="Contact")

@blog.route('/test',methods=['POST','GET'])
def test():
	
	return render_template('test.html')



@blog.route('/shop',methods=['POST','GET'])
def berkbuddy_shop():
	form = ShopSearch()
	if form.validate_on_submit():
		org = OrganizationDetails.query.filter((OrganizationDetails.link_name==form.shop_name.data.strip()) | 
			(OrganizationDetails.name==form.shop_name.data.strip())).first()
		return redirect(url_for('blog.home',link_name=org.link_name))
	return render_template('berk_shop.html',form=form,title="Shop")

@blog.route('/shopes')
def search_shopes():
	org = OrganizationDetails.query.all()
	list_shop = [o.as_dict() for o in org]
	return jsonify(list_shop)

@blog.route('/shop/<string:link_name>',methods=['GET','POST'])
def home(link_name):
	img_list={}
	form = feedback()
	org = OrganizationDetails.query.filter_by(link_name=link_name).first()
	if org==None:
		abort(404)
	user = org.org
	products = Product.query.filter_by(product=user,visible=0).all()
	re_products = Product.query.filter_by(product=user,visible=0).order_by(Product.date_edited.desc()).limit(10).all()
	mv_products = Product.query.filter((Product.product==user) & (Product.visible==0) & (Product.visit>0)).order_by(Product.visit.desc()).limit(10).all()
	mL_products = Product.query.filter((Product.product==user) & (Product.visible==0) & (Product.like>0)).order_by(Product.like.desc()).limit(10).all()
	bo_products = Product.query.filter((Product.product==user) & (Product.visible==0) & (Product.spl_cost>0)).order_by(Product.spl_cost.desc()).limit(10).all()
	search_form=ProductSearch()
	if search_form.validate_on_submit():
		search_product = Product.query.filter_by(product=user,visible=0,productname=search_form.product_name.data).first()
		if search_product == None:
			flash('Product not found','info')
		else:
			return redirect(url_for('blog.product',link_name=link_name,product_id=search_product.id))
	for product in products:
		img = ProductImage.query.filter_by(image=product).order_by(ProductImage.order).first()
		if img:
			img_list[product.id] = img.imagename
		else:
			img_list[product.id] = 'no_image_found.jpg'
	if form.validate_on_submit():
		if form.post.data:
			if not current_user.is_authenticated:
				return current_app.login_manager.unauthorized()
			feed = Feedback(org_id=org.id,ufeedback=current_user,feedback=form.feedback.data)
			form.feedback.data=""
			db.session.add(feed)
			db.session.commit()
			flash('Feedback posted','success')
	if request.method=='GET':
		org.visit = org.visit+1
		db.session.commit()
	return render_template('home.html',re_products=re_products,mv_products=mv_products,org=org,
							img_list=img_list,search_form=search_form,form=form,mL_products=mL_products,bo_products=bo_products)

@blog.route('/shop/<string:link_name>/category',methods=['GET','POST'])
def category(link_name):
	img_list={}
	org = OrganizationDetails.query.filter_by(link_name=link_name).first()
	if org==None:
		abort(404)
	user = org.org
	search_form=ProductSearch()
	if search_form.validate_on_submit():
		search_product = Product.query.filter_by(product=user,visible=0,productname=search_form.product_name.data).first()
		if search_product == None:
			flash('Product not found','info')
		else:
			return redirect(url_for('blog.product',link_name=link_name,product_id=search_product.id))
	categories = Folder.query.filter_by(folder=user,folderunder='0').all()
	return render_template('allproducts.html',org=org,categories=categories,search_form=search_form,
							img_list=img_list,folder_id=0,title='Products')

@blog.route('/shop/<string:link_name>/allproducts',methods=['GET','POST'])
def search_products(link_name):
	org = OrganizationDetails.query.filter_by(link_name=link_name).first()
	if org==None:
		abort(404)
	user = org.org
	products = Product.query.filter_by(product=user,visible=0).all()
	list_product = [p.as_dict() for p in products]
	return jsonify(list_product)

@blog.route('/shop/<string:link_name>/category/<int:folder_id>',methods=['GET','POST'])
def categoryper(link_name,folder_id):
	img_list={}
	org = OrganizationDetails.query.filter_by(link_name=link_name).first()
	if org==None:
		abort(404)
	user = org.org
	search_form=ProductSearch()
	if search_form.validate_on_submit():
		search_product = Product.query.filter_by(product=user,visible=0,productname=search_form.product_name.data).first()
		if search_product == None:
			flash('Product not found','info')
		else:
			return redirect(url_for('blog.product',link_name=link_name,product_id=search_product.id))
	cur_cat = Folder.query.get(folder_id)
	categories = Folder.query.filter_by(folder=user,folderunder=folder_id).all()
	products = Product.query.filter_by(product=user,productf=cur_cat,visible=0).order_by(Product.date_edited.desc()).all() 
	for product in products:
		img = ProductImage.query.filter_by(image=product).order_by(ProductImage.order).first()
		if img:
			img_list[product.id] = img.imagename
		else:
			img_list[product.id] = 'no_image_found.jpg'
	return render_template('allproducts.html',org=org,categories=categories,products=products,search_form=search_form,
							img_list=img_list,cur_cat=cur_cat,folder_id=folder_id,title='Products')

@blog.route('/shop/<string:link_name>/product/<int:product_id>',methods=['GET','POST'])
def product(link_name,product_id):
	org = OrganizationDetails.query.filter_by(link_name=link_name).first()
	if org==None:
		abort(404)
	user = org.org
	search_form=ProductSearch()
	if search_form.validate_on_submit():
		search_product = Product.query.filter_by(product=user,visible=0,productname=search_form.product_name.data).first()
		if search_product == None:
			flash('Product not found','info')
		else:
			if search_product.id!=product_id:
				return redirect(url_for('blog.product',link_name=link_name,product_id=search_product.id))
	product = Product.query.filter_by(product=user,id=product_id,visible=0).first()
	if product==None:
		abort(404)
	img_list = ProductImage.query.filter_by(image=product).order_by(ProductImage.order).all()
	like=None
	if current_user.is_authenticated:
		like = Likes.query.filter_by(org_id=org.id,like=product,ulikes=current_user).first()
	i=0
	offer_price = 0
	form = feedback()
	if product.spl_cost>0:
		offer_price = product.cost * (0.01) * (100-product.spl_cost)
	# if form.validate_on_submit:
	# 	if form.post.data:
	# 		if not current_user.is_authenticated:
	# 			return current_app.login_manager.unauthorized()
	# 		feed = Comments(comment=product,ucomment=current_user,comments=form.feedback.data,comment_id=0,org_id=org.id)
	# 		form.feedback.data=""
	# 		db.session.add(feed)
	# 		db.session.commit()
	# 		flash('Comment posted','success')
	if img_list:
		i = img_list[0].id
	if request.method=='GET':
		product.visit = product.visit+1
		db.session.commit()
	comments = Comments.query.filter_by(comment=product).order_by(Comments.date_posted).all()
	return render_template('blog_product.html',product=product,org=org,img_list=img_list,i=i,form=form,
		comments=comments,like=like,offer_price=offer_price,title=product.productname,search_form=search_form)


@blog.route('/shop/<string:link_name>/product/<int:product_id>/comment',methods=['POST','GET'])
@login_required
def comment(product_id,link_name):
	org = OrganizationDetails.query.filter_by(link_name=link_name).first()
	if org==None:
		abort(404)
	user = org.org
	product = Product.query.filter_by(product=user,id=product_id,visible=0).first()
	if product==None:
		abort(404)
	comment = request.get_json()
	if not current_user.is_authenticated:
		return current_app.login_manager.unauthorized()
	feed = Comments(comment=product,ucomment=current_user,comments=comment['comment'],comment_id=int(comment['comment_id']),org_id=org.id)
	db.session.add(feed)
	db.session.commit()
	return json.dumps({'status':'OK'})

@blog.route('/edit/<int:cmt_id>',methods=['POST','GET'])
@login_required
def edit_reply(cmt_id):
	cmt = Comments.query.get(cmt_id)
	if cmt==None:
		flash('invalid comment ID','info')
		return redirect(url_for('users.view_and_feedback'))
	if cmt.comment.product!=current_user:
		abort(403)
	form = Reply()
	if form.validate_on_submit():
		cmt.comments=form.comments.data
		db.session.commit()
		flash('Replied','success')
		return redirect(url_for('users.view_and_feedback'))
	if request.method=='GET':
		form.comments.data = cmt.comments
	return render_template('comment.html',form=form,title='Reply',cmt=cmt)



@blog.route('/delete_reply/<int:cmt_id>',methods=['POST','GET'])
@login_required
def delete_reply(cmt_id):
	cmt = Comments.query.get(cmt_id)
	if cmt==None:
		flash('invalid comment ID','info')
		return redirect(url_for('users.view_and_feedback'))
	if cmt.comment.product!=current_user:
		abort(403)
	db.session.delete(cmt)
	db.session.commit()
	return 'done'


@blog.route('/like/<string:link_name>/<int:product_id>',methods=['POST','GET'])
def like_ajax(product_id,link_name):
	if not current_user.is_authenticated:
		return json.dumps({"error": "Login Required"}),403
	product = Product.query.get(product_id)
	a_like = Likes.query.filter_by(like=product,ulikes=current_user).first()
	if a_like:
		flash('already liked','info')
		return redirect(url_for('blog.product', link_name=link_name,product_id=product_id))
	if product==None:
		abort(404)
	org = OrganizationDetails.query.filter_by(link_name=link_name).first()
	if org==None:
		abort(404)
	product.like = product.like + 1
	like = Likes(org_id=org.id,like=product,ulikes=current_user)
	db.session.add(like)
	db.session.commit()
	product = Product.query.get(product_id)
	return json.dumps({'status':'OK','like_count':product.like})

@blog.route('/berk/comment',methods=['POST','GET'])
def berk_comment():
	comment = request.get_json()
	feedback = Berk_Feedback(username=comment['name'],email=comment['email_id'],feedback=comment['comment'])
	db.session.add(feedback)
	db.session.commit()
	return json.dumps({'status':'OK'})