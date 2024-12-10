from flask_wtf import FlaskForm
from wtforms import StringField, ValidationError
from wtforms.validators import DataRequired


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
        # Check if tag with this name already exists
        from application.models import Tag

        existing_tag = Tag.query.filter(Tag.name == field.data).first()
        if existing_tag:
            raise ValidationError("A tag with this name already exists")

    name = StringField("Name", validators=[DataRequired()])
