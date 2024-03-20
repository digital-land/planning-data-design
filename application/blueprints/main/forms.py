from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired


class SpecificationForm(FlaskForm):
    specification_url = StringField(
        "URL",
        validators=[DataRequired()],
        description="Add a link to applicable specification",
    )
