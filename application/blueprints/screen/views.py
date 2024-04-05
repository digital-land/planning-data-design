from string import Template

from flask import Blueprint, redirect, render_template, url_for

from application.blueprints.screen.forms import (
    InputForm,
    SingleChoiceForm,
    SingleChoiceFormOther,
    TextareaForm,
)
from application.models import Consideration

screen = Blueprint(
    "screen",
    __name__,
    url_prefix="/planning-consideration/<consideration_slug>/screen",
)


questions = {
    "what-is-the-planning-consideration": {
        "question": Template("What is the '$name' consideration?"),
        "type": "textarea",
        "hint": """Provide a description of this planning consideration.
        The common name for the planning consideration should be used here""",
        "next": "is-there-legislation",
    },
    "is-there-legislation": {
        "question": Template("Is there legislation that defines '$name'?"),
        "type": "choose-one-from-list",
        "choices": [
            ("Yes", "Yes"),
            ("No", "No"),
        ],
        "hint": """Tell us where it is""",
        "prev": "what-is-the-planning-consideration",
        "next": "what-is-the-legislation-that-defines",
    },
    "what-is-the-legislation-that-defines": {
        "question": Template(
            "What is the legislation that defines how a '$name' gets designated?"
        ),
        "type": "textarea",
        "hint": """We are looking for the legislation that specifically sets out who,
        where applicable, are the parties who are able to designate the planning consideration""",
        "prev": "is-there-legislation",
        "next": "which-focus-area-does-it-support",
    },
    "what-is-the-legislation-for-publication": {
        "question": Template(
            "What is the legislation that requires the publication of  '$name'?"
        ),
        "type": "textarea",
        "hint": """We are looking for the legislation that specifically
        mentions data/registers or other""",
        "prev": "what-is-the-legislation-that-defines",
        "next": "who-in-law-is-responsible-for-it",
    },
    "who-in-law-is-responsible-for-it": {
        "question": Template(
            "Who, in law, is responsible for the planning consideration or makes decisions about '$name'?"
        ),
        "type": "textarea",
        "hint": """We are looking for the legislation that imposes this accountability on an organisation""",
        "prev": "what-is-the-legislation-for-publication",
        "next": "which-organisations-should-publish-it",
    },
    "which-organisations-should-publish-it": {
        "question": Template(
            "Which organisations do we think should publish '$name' data?"
        ),
        "type": "textarea",
        "hint": """This potentially is the same as the previous question, but if it is a SoS
        who is accountable it might be a clearly defined organisation""",
        "prev": "who-in-law-is-responsible-for-it",
    },
}


def _compile_template_strings(questions, consideration):
    # must be a better way to do this than each individul string
    for q_id, q_obj in questions.items():
        if isinstance(q_obj["question"], Template):
            q_obj["question"] = q_obj["question"].substitute(name=consideration.name)
    return questions


@screen.get("/")
def index(consideration_slug):
    consideration = Consideration.query.filter(
        Consideration.slug == consideration_slug
    ).first()

    return render_template(
        "questions/set.html",
        question_set="screen",
        consideration=consideration,
        questions=_compile_template_strings(questions, consideration),
        starting_question=next(iter(questions)),
    )


@screen.get("/<question_slug>")
def question(consideration_slug, question_slug):
    consideration = Consideration.query.filter(
        Consideration.slug == consideration_slug
    ).first()

    if question_slug not in questions.keys():
        return redirect(url_for("screen.index", consideration_slug=consideration_slug))

    question = questions[question_slug]
    if isinstance(question["question"], Template):
        question["question"] = question["question"].substitute(name=consideration.name)
    if question["type"] == "input":
        form = InputForm(label=question["question"])
        template = "questions/input.html"
    if question["type"] == "textarea":
        form = TextareaForm(label=question["question"])
        template = "questions/textarea.html"
    if question["type"] == "choose-one-from-list":
        form = SingleChoiceForm(label=question["question"])
        form.choice.choices = question["choices"]
        template = "questions/single-choice.html"
    if question["type"] == "choose-one-from-list-other":
        form = SingleChoiceFormOther(label=question["question"])
        form.choice.choices = question["choices"]
        template = "questions/single-choice.html"

    if form.validate_on_submit():
        pass

    return render_template(
        template,
        consideration=consideration,
        form=form,
        question=question,
        stage="screen",
    )
