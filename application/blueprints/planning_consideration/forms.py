from flask_wtf import FlaskForm
from wtforms import IntegerField, RadioField, StringField, TextAreaField, URLField
from wtforms.validators import DataRequired, Optional

from application.models import FrequencyOfUpdates, Stage


class LinkForm(FlaskForm):
    link_text = StringField("Title", validators=[DataRequired()])
    link_url = URLField("URL")

    def __init__(self, url_required=True, *args, **kwargs):
        super(LinkForm, self).__init__(*args, **kwargs)
        if url_required:
            self.link_url.validators = [DataRequired()]


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


class FrequencyForm(FlaskForm):
    frequency = RadioField(
        "How often do we expect this data to change?",
        validators=[DataRequired()],
        choices=[(freq.value, freq.value) for freq in FrequencyOfUpdates],
    )


class SynonymForm(FlaskForm):
    synonym = StringField(
        "Synonym",
        validators=[DataRequired()],
        description="Add another name people use for this planning consideration",
    )


class DeleteForm(FlaskForm):
    confirm = RadioField(
        "Are you sure you want to delete this?",
        validators=[DataRequired()],
        description="This is a destructive action. Be sure you want to permanently delete it.",
        choices=[("True", "Yes"), ("False", "No")],
    )


class ConsiderationForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    github_discussion_number = IntegerField(
        "Github disucssion number", validators=[Optional()]
    )
    description = TextAreaField("Description", validators=[Optional()])
    public_or_private = RadioField(
        "Public or private",
        validators=[DataRequired()],
        choices=[("public", "Public"), ("private", "Private")],
    )
