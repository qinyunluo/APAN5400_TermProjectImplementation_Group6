from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField
from wtforms.validators import DataRequired
import wtforms

boro_list = ["-- ALL --","Manhattan", "Bronx", "Brooklyn", "Queens", "Staten Island"]
critical_list = ["-- ALL --","Critical", "Not Critical"]
sorting_list = ["Inspection Date","Restaurant Name","Borough", "Zipcode", "Cuisine Type"]
order_list = ["Descending Order","Ascending Order"]

class SearchForm(FlaskForm):
    name = StringField('Restaurant Name [*required]', validators=[DataRequired()])
    startdate = DateField('Start Date [*required]', format='%Y-%m-%d')
    enddate = DateField('End Date [*required]', format='%Y-%m-%d')
    zipcode = StringField('Zipcode')
    boro = wtforms.SelectField(label='Borough', 
        choices=[(boro, boro) for boro in boro_list])
    critical = wtforms.SelectField(label='Critical Level', 
        choices=[(critical, critical) for critical in critical_list])
    sorting = wtforms.SelectField(label='Sorting By', 
        choices=[(sorting, sorting) for sorting in sorting_list])
    order = wtforms.SelectField(label='Sorting Order', 
        choices=[(order, order) for order in order_list])    
    submit = SubmitField('Search')
