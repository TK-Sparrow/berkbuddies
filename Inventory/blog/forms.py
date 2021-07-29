from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,TextAreaField,SelectField
from wtforms.validators import DataRequired,Length,ValidationError
from inventory.models import OrganizationDetails,User


class ShopSearch(FlaskForm):
	shop_name = StringField('Shop Name or Link Name',validators=[DataRequired()])
	search = SubmitField('Search')

	def validate_shop_name(self,shop_name):
		org = OrganizationDetails.query.filter((OrganizationDetails.link_name==shop_name.data.strip()) | 
			(OrganizationDetails.name==shop_name.data.strip())).first()
		if org==None:
			raise ValidationError('Sorry Requested Shop is Not Available!')

class ProductSearch(FlaskForm):
	product_name = StringField('Search br Product Name')
	search = SubmitField('Search')

		
class feedback(FlaskForm):
	feedback = StringField("Feedback",validators=[DataRequired(),Length(min=3,max=100)])
	post = SubmitField("Post")


class Reply(FlaskForm):
	comment = StringField('Reply Comment',validators=[DataRequired()])
	submit = SubmitField("Reply")
class EdmundsForm(FlaskForm):
    year = SelectField('year', choices =[('1990', '1990'), ('1991', '1991'), ('1992', '1992'),    ('1993', '1993'), ('1994', '1994'),
    ('1995', '1995'), ('1996', '1996'), ('1997', '1997'), ('1998', '1998'), ('1999', '1999'), ('2000', '2000'), ('2001', '2001'),
    ('2002', '2002'), ('2003', '2003'), ('2004', '2004'), ('2005', '2005'), ('2006', '2006'), ('2007', '2007'), ('2008', '2008'),
    ('2009', '2009'), ('2010', '2010'), ('2011', '2011'), ('2012', '2012'), ('2013', '2013'), ('2014', '2014'), ('2015', '2015'),
    ('2016', '2016')])
    make = SelectField('make', choices = [])