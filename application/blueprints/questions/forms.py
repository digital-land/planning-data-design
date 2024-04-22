from flask_wtf import FlaskForm
from wtforms import RadioField, StringField, TextAreaField, URLField


class TextareaForm(FlaskForm):
    input = TextAreaField("Title")

    def __init__(self, label="Title", *args, **kwargs):
        super(TextareaForm, self).__init__(*args, **kwargs)
        self.input.label.text = label


class InputForm(FlaskForm):
    input = StringField("Title")

    def __init__(self, label="Title", *args, **kwargs):
        super(InputForm, self).__init__(*args, **kwargs)
        self.input.label.text = label


class SingleChoiceForm(FlaskForm):
    choice = RadioField("Pick one")

    def __init__(self, label="Pick one", *args, **kwargs):
        super(SingleChoiceForm, self).__init__(*args, **kwargs)
        self.choice.label.text = label


class SingleChoiceFormOther(FlaskForm):
    choice = RadioField("Pick one")
    other = StringField("Other")

    def __init__(self, label="Title", *args, **kwargs):
        super(SingleChoiceFormOther, self).__init__(*args, **kwargs)
        self.choice.label.text = label


class LifecycleStagesForm(FlaskForm):
    name = StringField("Stage name")
    description = TextAreaField("Description")
    actors = StringField("Who is involved?")
    output = TextAreaField("What is produced?")
    impact = TextAreaField("Impact")


class ExistingDataForm(FlaskForm):
    publisher = StringField("Publisher", description="Who publishes the data?")
    url = URLField("URL", "A url for the data")
    fields = StringField(
        "Fields",
        description="List the fields included in the data. Separate the fields with a ;",
    )
    licence = StringField(
        "Licence", description="Include the licence the data has been published under."
    )
    attribution = TextAreaField(
        "Attribution",
        description="If attribution is needed to use the data include it here.",
    )
    coverage = StringField(
        "Coverage",
        description="Whats the coverage of the dataset? For example, national, partial, local authority area, etc",
    )
