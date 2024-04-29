from flask_wtf import FlaskForm
from wtforms import RadioField
from wtforms.validators import DataRequired


class DeleteForm(FlaskForm):
    confirm = RadioField(
        "Are you sure you want to delete this?",
        validators=[DataRequired()],
        description="This is a destructive action. Be sure you want to permanently delete it.",
        choices=[("True", "Yes"), ("False", "No")],
    )
