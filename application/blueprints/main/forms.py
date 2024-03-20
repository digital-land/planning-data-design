from flask_wtf import FlaskForm
from wtforms import IntegerField, RadioField, StringField
from wtforms.validators import DataRequired


class SpecificationForm(FlaskForm):
    specification_url = StringField(
        "URL",
        validators=[DataRequired()],
        description="Add a link to applicable specification",
    )


class LinkForm(FlaskForm):
    link_text = StringField("Title", validators=[DataRequired()])
    link_url = StringField("URL", validators=[DataRequired()])


class ExpectedSizeForm(FlaskForm):
    expected_number_of_records = IntegerField(
        "Expected number of records",
        description="Put an estimate for expected number of records. For example, 100 or 25,0000",
    )
    input_size = "10"


class PriorityForm(FlaskForm):
    prioritised = RadioField(
        "Are we prioritising this planning consideration?",
        validators=[DataRequired()],
        description="Prioritised items will show up in our list of working on or emerging priorities",
        choices=[("True", "Yes"), ("False", "No")],
    )
