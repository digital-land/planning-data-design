from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, TextAreaField
from wtforms.validators import DataRequired, Optional


class ConsiderationForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    github_discussion_number = IntegerField(
        "Github disucssion number", validators=[Optional()]
    )
    description = TextAreaField("Description", validators=[Optional()])
