from flask_wtf import FlaskForm
from wtforms import IntegerField, RadioField, StringField, TextAreaField
from wtforms.validators import DataRequired, Optional

from application.models import Stage


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


class PublicForm(FlaskForm):
    public = RadioField(
        "Should the work we do on this planning consideration be public?",
        validators=[DataRequired()],
        description="Things not marked public will not show in the public list of planning considerations.",
        choices=[("True", "Yes"), ("False", "No")],
    )


class StageForm(FlaskForm):
    stage = RadioField(
        "What stage are we at with this planning consideration?",
        validators=[DataRequired()],
        description="We should only change the stage when we are confident we have enough information to move on.",
        choices=[(stage.value, stage.value) for stage in Stage],
    )
    reason = TextAreaField("Reason for changing the stage", validators=[Optional()])
