from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired

class SignupForm(FlaskForm):
    name = StringField('name', validators=[DataRequired()])
    email = StringField('email', validators=[DataRequired()])

