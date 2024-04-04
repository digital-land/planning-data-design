from flask_wtf import FlaskForm
from wtforms import RadioField, StringField, TextAreaField


class TextareaForm(FlaskForm):
    input = TextAreaField("Title")

    def __init__(self, label="Title", *args, **kwargs):
        super(InputForm, self).__init__(*args, **kwargs)
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
