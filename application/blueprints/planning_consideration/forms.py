from flask import flash, url_for
from flask_wtf import FlaskForm
from markupsafe import Markup
from slugify import slugify
from wtforms import (
    IntegerField,
    RadioField,
    StringField,
    TextAreaField,
    URLField,
    ValidationError,
)
from wtforms.validators import DataRequired, Optional

from application.models import FrequencyOfUpdates, OSDeclarationStatus, Stage


class DatasetForm(FlaskForm):
    dataset = URLField("Dataset schema URL", validators=[DataRequired()])


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


class LLCForm(FlaskForm):
    is_local_land_charge = RadioField(
        "Is this consideration also a type of local land charge?",
        validators=[DataRequired()],
        choices=[("True", "Yes"), ("False", "No")],
    )


class LocalPlanDataForm(FlaskForm):
    is_local_plan_data = RadioField(
        "Is this consideration used in local plans?",
        validators=[DataRequired()],
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


class OSDeclarationForm(FlaskForm):
    status = RadioField(
        "What is the status of the OS declaration?",
        validators=[DataRequired()],
        description="The declaration should match what we've discussed with OS",
        choices=[(status.value, status.value) for status in OSDeclarationStatus],
    )
    further_information_url = URLField("URL to further information")


class FrequencyForm(FlaskForm):
    frequency_of_updates = RadioField(
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


def unique_name_validator(form, name):
    from application.models import Consideration

    slug = slugify(name.data)
    consideration = Consideration.query.filter_by(slug=slug).one_or_none()
    if consideration is not None:
        if all(
            [
                form[p].data
                == (
                    str(getattr(consideration, p))
                    if p == "public"
                    else getattr(consideration, p)
                )
                for p in ["github_discussion_number", "public", "description"]
            ]
        ):
            url = url_for("planning_consideration.consideration", slug=slug)
            message = Markup(
                (
                    f"The planning consideration might have been archived. "
                    f"Go to existing consideration <a href='{url}'>{consideration.name}</a> "
                    "and change the stage to bring it back."
                )
            )
            flash(message)
            raise ValidationError(
                f"The consideration '{consideration.name}' already exists."
            )


class ConsiderationForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), unique_name_validator])
    github_discussion_number = IntegerField(
        "Github discussion number", validators=[Optional()]
    )
    description = TextAreaField("Description", validators=[Optional()])
    public = RadioField(
        "Public or private",
        validators=[DataRequired()],
        choices=[("True", "Public"), ("False", "Private")],
        default="True",
    )


class NoteForm(FlaskForm):
    text = TextAreaField("Note", validators=[DataRequired()])


class BlockedForm(FlaskForm):
    reason = TextAreaField(
        "Reason for marking planning consideration as blocked",
        validators=[DataRequired()],
    )
