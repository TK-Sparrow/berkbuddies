from flask import render_template,url_for,Blueprint,redirect,flash,request,session,json,current_app
from flask_login import login_user,current_user,logout_user,login_required
from inventory.users.forms import (RegistrationForm,RegisterMail,LoginForm,RequestResetForm,ResetPasswordForm,
						mobile_verification,OTP_verification,account_form,organization_form,Reply)
from inventory.users.utility import (send_register_email,verify_register_token,send_resent_email,
						start_verification,check_verification,save_picture,to_s3)
from inventory.models import User,OrganizationDetails,Feedback,Product,Comments,Folder,Likes
from inventory import bcrypt,db
#from urllib.request import urlopen
from urllib.request import Request, urlopen


users = Blueprint('users',__name__)


@users.route("/register",methods=['POST','GET'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('products.dashboard'))
	form = RegisterMail()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user:
			 flash('Already registered using this mail.', 'info')
			 return redirect(url_for('users.register'))
		send_register_email(form.email.data)
		flash('An email has been sent with instructions to Continue the registration.', 'info')
		return redirect(url_for('users.register'))
	return render_template('register_mail.html',form=form, title="Register")


@users.route("/continue_register/<token>",methods=['GET','POST'])
def continue_register(token):
	if current_user.is_authenticated:
		return redirect(url_for('products.dashboard'))
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user = User(username=form.username.data, email=form.email.data, password=hashed_password)
		db.session.add(user)
		db.session.commit()
		flash('Your account has been created! You are now able to log in', 'success')
		return redirect(url_for('users.login'))
	email = verify_register_token(token)
	if email is None:
		flash('Invlaid Token','warning')
		return redirect(url_for('users.register'))		
	user = User.query.filter_by(email=email).first()
	if user:
		flash('Already Register using this email','info')
		return redirect(url_for('users.login'))
	form.email.data=email
	return render_template('register.html',form=form,title="Register")
	
@users.route("/login" ,methods=['GET','POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('products.dashboard'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user and bcrypt.check_password_hash(user.password,form.password.data):
			login_user(user)
			session.pop('folder',None)
			next_page = request.args.get('next')
			url = url_for('blog.berkbuddy_home')
			if next_page:
				url = next_page
			return redirect(url)
		else:
			flash('Invalid Credentials','danger')
	return render_template("login.html",form=form,title="login")

@users.route("/login_refresh" ,methods=['GET','POST'])
def login_refresh():
	url = request.referrer
	if not current_user.is_authenticated:
		session['previous_page'] = request.referrer
		return current_app.login_manager.unauthorized()
	if 'previous_page' in session:
		url = session['previous_page']
	return redirect(url)

@users.route("/reset_password",methods=['GET','POST'])
def reset_password():
	if current_user.is_authenticated:
		return redirect(url_for('products.dashboard'))
	form = RequestResetForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		send_resent_email(form.email.data)
		flash('Link has been send to your mail to change your password','info')
		return redirect(url_for('users.login'))
	return render_template('request_password.html',form=form,title='Reset Password')

@users.route("/reset_password/<token>",methods=['POST','GET'])
def change_password(token):
	if current_user.is_authenticated:
		return redirect(url_for('products.dashboard'))
	email = verify_register_token(token)
	if email is None:
		flash('That is an invalid or expired token', 'warning')
		return redirect(url_for('users.reset_password'))
	user = User.query.filter_by(email=email).first()
	form = ResetPasswordForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user.password = hashed_password
		db.session.commit()
		flash('Your password has been updated! You are now able to log in', 'success')
		return redirect(url_for('users.login'))
	return render_template('reset_password.html',form=form,title='Reset Password')

@users.route("/logout")
def logout():
	logout_user()
	return redirect(request.referrer)


@users.route("/mobile_number_verification",methods=['GET','POST'])
@login_required
def mobile_number_verification():
	form = mobile_verification()
	if form.validate_on_submit():
		code = "+"+form.country_code.data
		mobile_number = form.mobile_number.data
		user = User.query.filter_by(mobile_number=code+str(mobile_number)).first()
		if user:
			flash("Mobile number already exist Try some other",'danger')
			return render_template('mobile_register.html',form=form,title='Register Mobile number')
		vsid = start_verification(code+str(mobile_number))
		if vsid is not None:
			session['mobile_number']=code+str(mobile_number)
			flash('OTP has been send to the registered number', 'success')
			return redirect(url_for('users.code_verification'))
		else:
			return("none")
	return render_template('mobile_register.html',form=form,title='Register Mobile number')

@users.route("/code_verification",methods=['GET','POST'])
@login_required
def code_verification():
	form = OTP_verification()
	if form.validate_on_submit():
		mobile_number = session['mobile_number']
		session.pop('mobile_number',None)
		vsid = check_verification(mobile_number,form.OTP.data)
		if vsid is not None:
			current_user.mobile_number = mobile_number
			db.session.commit()
			flash('Your mobile number has been updated!', 'success')
			return redirect(url_for('users.profile'))
		else:
			flash('Verification Failed Try Again', 'danger')
			return redirect(url_for('users.profile'))
	return render_template("otp_verify.html",form=form,title='Register Mobile number')

@users.route("/profile",methods=["GET","POST"])
@login_required
def profile():
	form = account_form()
	if form.validate_on_submit():
		current_user.username = form.username.data
		db.session.commit()
		flash('Your profile has been updated!', 'success')
		return redirect(url_for('users.profile'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email
		form.mobile_number.data = current_user.mobile_number
	date = current_user.account_created
	return render_template('profile.html',form=form,date=date,title='Profile')

@users.route('/organization/create',methods=['GET','POST'])
@login_required
def org_create():
	if current_user.mobile_number == 'none' or current_user.mobile_number == None:
		flash('Verify your mobile number to access My Org','info')
		return redirect(url_for('users.mobile_number_verification'))
	org = OrganizationDetails.query.filter_by(org=current_user).first()
	if org:
		return redirect(url_for("users.org_details"))
	form = organization_form()
	if form.validate_on_submit():
		picture_file="no_image_found.jpg"
		if form.logo.data:
			#picture_file = save_picture(form.logo.data,"org_logo")
			picture_file = to_s3(request.files['logo'],"org_logo")
		org = OrganizationDetails(name=form.org_name.data,category=form.category.data,address=form.address.data,city=form.city_name.data
									,state=form.state_name.data,country=form.country_name.data,pincode=form.pincode.data
									,about=form.about.data,slogan=form.slogan.data,logo=picture_file
									,insta=form.insta.data,facebook=form.facebook.data
									,link_name=form.link_name.data,org=current_user,
									color_code1=form.background_color1.data,color_code2=form.background_color2.data)
		db.session.add(org)
		db.session.commit()
		flash("Your organization has been created","success")
		return redirect(url_for("users.org_details"))
	return render_template('org_details.html',form=form,title='My Org Create')


@users.route('/organization',methods=['GET','POST'])
@login_required
def org_details():
	if current_user.mobile_number == 'none' or current_user.mobile_number == None:
		flash('Verify your mobile number to access My Org','info')
		return redirect(url_for('users.mobile_number_verification'))
	org = OrganizationDetails.query.filter_by(org=current_user).first()
	if org==None:
		return redirect(url_for("users.org_create"))
	return render_template('org_display.html',org=org,title='My Org')


@users.route('/organization/update',methods=['GET','POST'])
@login_required
def org_update():
	if current_user.mobile_number == 'none' or current_user.mobile_number == None:
		flash('Verify your mobile number to access My Org','info')
		return redirect(url_for('users.mobile_number_verification'))
	org = OrganizationDetails.query.filter_by(org=current_user).first()
	if org==None:
		return redirect(url_for("users.org_create"))
	form = organization_form()
	if form.validate_on_submit():
		if form.unpublish.data:
			org.visible = 1
			flash('Your Organization is not visible to others','success')
			db.session.commit()
		elif form.publish.data:
			org.visible = 0
			flash('Your Organization is visible to others','success')
			db.session.commit()
		else:
			picture_file=org.logo
			if form.logo.data:
				#picture_file = save_picture(form.logo.data,"org_logo")
				picture_file = to_s3(request.files['logo'],"org_logo")
			org.name=form.org_name.data
			org.address=form.address.data
			org.city=form.city_name.data
			org.state=form.state_name.data
			org.country=form.country_name.data
			org.pincode=form.pincode.data
			org.about=form.about.data
			org.slogan=form.slogan.data
			org.insta=form.insta.data
			org.category = form.category.data
			org.facebook=form.facebook.data
			org.logo=picture_file
			org.link_name=form.link_name.data
			org.color_code1=form.background_color1.data
			org.color_code2=form.background_color2.data
			db.session.commit()
			flash('organization details nas been updated','success')
			return redirect(url_for("users.org_details"))

	elif request.method == 'GET':
		form.org_name.data = org.name
		form.address.data = org.address
		form.city_name.data = org.city
		form.state_name.data = org.state
		form.category.data = org.category
		form.country_name.data = org.country
		form.pincode.data = org.pincode
		form.about.data = org.about
		form.slogan.data = org.slogan
		form.facebook.data = org.facebook
		form.insta.data = org.insta
		form.link_name.data = org.link_name
		form.background_color1.data = org.color_code1
		form.background_color2.data = org.color_code2
	return render_template('org_details.html',form=form,title='My Org Update')


@users.route('/country',methods=['POST','GET'])
def country():
	req = Request('https://geodata.solutions/restapi?dd=1', headers={'User-Agent': 'Mozilla/5.0'})
	url = urlopen(req)
	#url = urlopen('https://geodata.solutions/restapi?dd=1')
	result = json.loads(url.read())
	country='''<select id="country" name="country" onchange="states()" class="form-control form-control-lg">'''
	for re in result:
		country=country+'''<option value="{val_id}">{val_val}</option>'''.format(val_id=re[0],val_val=re[1])
	country=country+"</select>"
	return json.dumps({'country':country})

@users.route('/state/<string:country_name>',methods=['POST','GET'])
def state(country_name):
	req = Request('https://geodata.solutions/restapi?dd=1&country='+country_name, headers={'User-Agent': 'Mozilla/5.0'})
	url = urlopen(req)
	#url = urlopen('https://geodata.solutions/restapi?dd=1&country='+country_name)
	result = json.loads(url.read())
	state='''<select id="state" name="state" onchange="cities()" class="form-control form-control-lg">'''
	for re in result:
		state=state+'''<option value="{val_id}">{val_val}</option>'''.format(val_id=re[0],val_val=re[1])
	state=state+"</select>"
	return json.dumps({'state':state})

@users.route('/city/<string:country_name>/<string:state_name>',methods=['POST','GET'])
def city(country_name,state_name):
	city_dict={}
	req = Request('https://geodata.solutions/restapi?dd=1&country='+country_name+'&state='+state_name, headers={'User-Agent': 'Mozilla/5.0'})
	url = urlopen(req)
	#url = urlopen('https://geodata.solutions/restapi?dd=1&country='+country_name+'&state='+state_name)
	result = json.loads(url.read())
	city='''<select id="city" name="city" class="form-control form-control-lg">'''
	for re in result:
		city_dict[re[0]]=re[1]		
	sort_orders = sorted(city_dict.items(), key=lambda x: x[1], reverse=False)
	for x in sort_orders:
		city=city+'''<option value="{val_id}">{val_val}</option>'''.format(val_id=x[0],val_val=x[1])
	city=city+"</select>"
	return json.dumps({'city':city})


@users.route('/dashboard',methods=['POST','GET'])
@login_required
def view_and_feedback():
	org = OrganizationDetails.query.filter_by(org=current_user).first()
	if org == None:
		flash('Create org to view Dashboard','info')
		return redirect(url_for('products.dashboard'))
	folders = Folder.query.filter_by(folder=current_user).all()
	products = Product.query.filter_by(product=current_user).order_by(Product.date_edited.desc()).all()
	mv_product = Product.query.filter_by(product=current_user).order_by(Product.visit.desc()).first()
	ml_product = Product.query.filter_by(product=current_user).order_by(Product.like.desc()).first()
	feedbacks = Feedback.query.filter_by(org_id=org.id).order_by(Feedback.date_posted.desc()).all()
	comments = Comments.query.filter_by(org_id=org.id).order_by(Comments.date_posted.desc()).all()
	likes = Likes.query.filter_by(org_id=org.id).order_by(Likes.date_liked.desc()).all()
	v=0;
	if products:
		for product in products:
			v=v+product.visit
	avg_pv=0
	if v!=0:
		avg_pv=int(v/len(products))
	return render_template('visit_and_feedback.html',org=org,products=products,feedbacks=feedbacks,comments=comments,
							p_count=len(products),c_count=len(folders),mv_product=mv_product,ml_product=ml_product,
							avg_pv=avg_pv,likes=likes,title='Dashboard')


@users.route('/dashboard_refresh',methods=['POST','GET'])
@login_required
def view_and_feedback_refresh():
	org = OrganizationDetails.query.filter_by(org=current_user).first()
	if org == None:
		flash('Create org to visit Dashboard','info')
		return redirect(url_for('products.dashboard'))
	folders = Folder.query.filter_by(folder=current_user).all()
	products = Product.query.filter_by(product=current_user).order_by(Product.date_edited.desc()).all()
	mv_product = Product.query.filter_by(product=current_user).order_by(Product.visit.desc()).first()
	ml_product = Product.query.filter_by(product=current_user).order_by(Product.like.desc()).first()
	feedbacks = Feedback.query.filter_by(org_id=org.id).order_by(Feedback.date_posted.desc()).all()
	comments = Comments.query.filter_by(org_id=org.id).order_by(Comments.date_posted.desc()).all()
	likes = Likes.query.filter_by(org_id=org.id).order_by(Likes.date_liked.desc()).all()
	v=0;
	if products:
		for product in products:
			v=v+product.visit
	avg_pv=0
	if v!=0:
		avg_pv=int(v/len(products))
	product_string='''<table class="table table-striped table-sm">
	          <thead>
	            <tr>
	              <th>Name</th>
	              <th>Cost</th>
	              <th>Offer %</th>
	              <th>Quantity</th>
	              <th>Visit</th>
	              <th>Like</th>
	              <th>Published</th>
	            </tr>
	          </thead>
	          <tbody>'''
	if products:
		for product in products:
			product_string=product_string+'''<tr>
	              <td><a href="{url}" class="btn 
	              	btn-link">{productname}</a></td>
	              <td>{cost}</td>
	              <td>{spl_cost}%</td>
	              <td>{quantity}</td>
	              <td>{visit}</td>
	              <td>{like}</td>
	              <td>'''.format(url=url_for('products.update_product',product_id=product.id), productname=product.productname,
	              				cost=product.cost, spl_cost=product.spl_cost,quantity=product.quantity,
	              				visit=product.visit,like=product.like)

			if product.visible==0:
				product_string=product_string+"yes"
			else:
				product_string=product_string+"No"
			product_string=product_string+"</td></tr>"
	else:
		product_string=product_string+"<h6>No Products to Show </h6>"
	product_string=product_string+"</tbody></table>"
	feedback_string = ""
	if feedbacks:
		for feedback in feedbacks:
			feedback_string =feedback_string + '''<div class="row border-bottom border-dark">
	  		<div class="col-md-auto">
	  			<h6>{username}:</h6>
	  			<small>{date_posted}</small>
	  		</div>
	  		<div class="col">
	  			{feedback}
	  		</div>  		
	  	</div>'''.format(username=feedback.ufeedback.username,date_posted=feedback.date_posted,feedback=feedback.feedback)
	else:
	 	feedback_string="<h6>No Feedbacks to Show </h6>"
	comment_string = '''<table class="table table-striped table-sm">
	          <thead>
	            <tr>
	              <th>Username</th>
	              <th>Product Name</th>
	              <th>Comment</th>
	              <th>Date posted</th>
	              <th>Reply</th>

	            </tr>
	          </thead>
	          <tbody>
					'''
	if comments:
		for comment in comments:
			comment_string=comment_string+'''<tr>
	              <td>{username}</td>
	              <td><a href="{url}" class="btn 
	              	btn-link">{productname}</a></td>
	              <td>{comment}</td>
	              <td>{date_posted}</td>
	              <td><a target="_blank" href="{v_url}">View</a></td>
	            </tr>'''.format(username=comment.ucomment.username,url=url_for('products.update_product',product_id=comment.comment.id),
	            	productname=comment.comment.productname,comment=comment.comments,date_posted=comment.date_posted,
	            	v_url=url_for('blog.product', link_name=org.link_name,product_id=comment.comment.id)+"#cmt")
	else:
		comment_string=comment_string+"<h6>No Comments to Show </h6>"
	comment_string = comment_string +"</tbody></table>"
	like_string='''<table class="table table-striped table-sm">
	          <thead>
	            <tr>
	              <th>Username</th>
	              <th>Product Name</th>
	              <th>Date Liked</th>

	            </tr>
	          </thead>
	          <tbody>'''
	if likes:
		for like in likes:
			like_string = like_string + '''<tr>
	              <td>{liked}</td>
	              <td><a href="{url}" class="btn 
	              	btn-link">{productname}</a></td>
	              <td>{date_liked}</td>
	            </tr>'''.format(liked=like.ulikes.username,url=url_for('products.update_product',product_id=like.like.id),
	            				productname=like.like.productname,date_liked=like.date_liked)
	else:
		like_string = like_string + "<h6>No Like to Show </h6>"
	like_string = like_string + "</tbody></table>"
	return json.dumps({'products':product_string,'feedbacks':feedback_string,'comments':comment_string,
						'likes':like_string,'p_count':len(products),'c_count':len(folders),'mv_product_name':mv_product.productname,
						'mv_product_view':mv_product.visit,'ml_product_name':ml_product.productname,'ml_product_like':ml_product.like,'avg_pv':avg_pv,'org_visit':org.visit})







	          	