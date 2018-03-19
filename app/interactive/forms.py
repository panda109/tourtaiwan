# app/admin/forms.py

from datetime import datetime
from app import FlaskForm
from wtforms import SubmitField, BooleanField, validators
from wtforms.validators import DataRequired
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from ..models import Car_type, Tour_type
from wtforms.fields.html5 import DateField
class InteractiveForm(FlaskForm):
    """
    Form for admin to add or edit a department
    """
    car_type = QuerySelectField(query_factory=lambda: Car_type.query.all(), get_label="car_name")
    tour_type = QuerySelectField(query_factory=lambda: Tour_type.query.all(), get_label="tour_name")
    tour_date = DateField('StartDate : ', validators=[DataRequired()])
    tour_guide = BooleanField('Tour_guide(English)', default=False)
    submit = SubmitField('Submit')
    