from string import Template

from flask import Blueprint, redirect, render_template, url_for

from application.blueprints.backlog.forms import (
    InputForm,
    SingleChoiceForm,
    SingleChoiceFormOther,
)
from application.models import Consideration

backlog = Blueprint(
    "backlog",
    __name__,
    url_prefix="/planning-consideration/<consideration_slug>/backlog",
)


questions = {
    "who-asked-for-it": {
        "question": Template("Who asked for $name data?"),
        "type": "input",
        "next": "what-is-the-driver",
    },
    "what-is-the-driver": {
        "question": "What is the driver for the request?",
        "type": "choose-one-from-list",
        "choices": [
            ("National policy change", "National policy change"),
            ("Ministerial priority", "Ministerial priority"),
            ("Specific user requirement", "Specific user requirement"),
            ("LPA requirement", "LPA requirement"),
            ("Existing planning requirement", "Existing planning requirement"),
        ],
        "next": "which-focus-area-does-it-support",
    },
    "which-focus-area-does-it-support": {
        "question": "Which 2024 focus area does the request support?",
        "type": "choose-one-from-list-other",
        "choices": [
            ("Modern planning software", "Modern planning software"),
            ("Faster local plans", "Faster local plans"),
            ("Included in LURA", "Included in LURA"),
            ("Other", "Other"),
        ],
    },
}


@backlog.get("/")
def index(consideration_slug):
    consideration = Consideration.query.filter(
        Consideration.slug == consideration_slug
    ).first()

    return render_template(
        "questions/set.html",
        question_set="Backlog",
        consideration=consideration,
        questions=questions,
        starting_question=next(iter(questions)),
    )


@backlog.get("/<question_slug>")
def question(consideration_slug, question_slug):
    consideration = Consideration.query.filter(
        Consideration.slug == consideration_slug
    ).first()

    if question_slug not in questions.keys():
        return redirect(url_for("backlog.index", consideration_slug=consideration_slug))

    question = questions[question_slug]
    if isinstance(question["question"], Template):
        question["question"] = question["question"].substitute(name=consideration.name)

    if question["type"] == "input":
        form = InputForm(label=question["question"])
        template = "questions/input.html"
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
    )
