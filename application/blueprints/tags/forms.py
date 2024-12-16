from flask import request
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, ValidationError
from wtforms.validators import DataRequired

from application.models import Tag


class TagForm(FlaskForm):
    def sanitize_tag_name(self, field):
        if field.data:
            # Remove leading/trailing whitespace and collapse internal whitespace
            sanitized = " ".join(field.data.split())
            # Capitalize first letter, lowercase rest
            field.data = (
                sanitized[0].upper() + sanitized[1:].lower() if sanitized else ""
            )

    def validate_name(self, field):
        self.sanitize_tag_name(field)
        existing_tag = Tag.query.filter(Tag.name == field.data).first()
        if existing_tag:
            # If we're editing an existing tag (URL has tag_id) and the name hasn't changed,
            # then this is valid - it's the same tag
            tag_id = request.view_args.get("tag_id")
            if not tag_id or str(existing_tag.id) != tag_id:
                raise ValidationError("A tag with this name already exists")

    name = StringField("Name", validators=[DataRequired()])


class AddTagForm(FlaskForm):
    new_tag = SelectField("New tag", validators=[DataRequired()])
