from flask import Blueprint, redirect, render_template, url_for

from application.blueprints.questions.forms import (
    InputForm,
    SingleChoiceForm,
    SingleChoiceFormOther,
    TextareaForm,
)
from application.models import Answer, Consideration, Question, QuestionType

questions = Blueprint(
    "questions",
    __name__,
    url_prefix="/planning-consideration/<string:consideration_slug>/<stage:stage>",
)


@questions.get("/")
def index(consideration_slug, stage):
    consideration = Consideration.query.filter(
        Consideration.slug == consideration_slug
    ).first()

    questions = Question.query.filter(Question.stage == stage).all()

    return render_template(
        "questions/set.html",
        stage=stage,
        consideration=consideration,
        questions=questions,
        starting_question=next(iter(questions)),
    )


@questions.get("/<question_slug>")
def question(consideration_slug, stage, question_slug):
    consideration = Consideration.query.filter(
        Consideration.slug == consideration_slug
    ).first()

    question = Question.query.filter(
        Question.stage == stage, Question.slug == question_slug
    ).one_or_none()

    if question is None:
        return redirect(
            url_for(
                "questions.index", consideration_slug=consideration_slug, stage=stage
            )
        )

    label = question.format(consideration.name)
    answer = consideration.get_answer(question)

    match question.question_type:
        case QuestionType.INPUT:
            form = InputForm(label=label)
            form.input.data = answer.text if answer else ""
            template = "questions/input.html"
        case QuestionType.TEXTAREA:
            form = TextareaForm(label=label)
            template = "questions/textarea.html"
            form.input.data = answer.text if answer else ""
        case QuestionType.CHOOSE_ONE_FROM_LIST:
            form = SingleChoiceForm(label=label)
            form.choice.choices = [(choice, choice) for choice in question.choices]
            form.choice.data = answer.text if answer else ""
            template = "questions/single-choice.html"
        case QuestionType.CHOOSE_ONE_FROM_LIST_OTHER:
            form = SingleChoiceFormOther(label=label)
            form.choice.choices = [(choice, choice) for choice in question.choices]
            form.choice.data = answer.text if answer else ""
            template = "questions/single-choice.html"
        case _:
            return redirect(
                url_for(
                    "questions.index",
                    consideration_slug=consideration_slug,
                    stage=stage,
                )
            )

    return render_template(
        template,
        consideration=consideration,
        form=form,
        question=question,
        stage=stage,
    )


@questions.post("/<question_slug>")
def save_answer(consideration_slug, stage, question_slug):
    from application.extensions import db

    consideration = Consideration.query.filter(
        Consideration.slug == consideration_slug
    ).one_or_404()

    question = Question.query.filter(
        Question.stage == stage, Question.slug == question_slug
    ).one_or_none()

    if question is None:
        return redirect(
            url_for(
                "questions.index", consideration_slug=consideration_slug, stage=stage
            )
        )

    match question.question_type:
        case QuestionType.INPUT:
            form = InputForm()
            data = form.input.data
        case QuestionType.TEXTAREA:
            form = TextareaForm()
            data = form.input.data
        case QuestionType.CHOOSE_ONE_FROM_LIST:
            form = SingleChoiceForm()
            form.choice.choices = [(choice, choice) for choice in question.choices]
            data = form.choice.data
        case QuestionType.CHOOSE_ONE_FROM_LIST_OTHER:
            form = SingleChoiceFormOther()
            form.choice.choices = [(choice, choice) for choice in question.choices]
            data = form.choice.data
        case _:
            return redirect(
                url_for(
                    "questions.index",
                    consideration_slug=consideration_slug,
                    stage=stage,
                )
            )

    if form.validate_on_submit():
        answer = Answer.query.filter(
            Answer.consideration_id == consideration.id,
            Answer.question_slug == question.slug,
        ).one_or_none()
        if answer is None:
            answer = Answer(
                text=data,
                consideration_id=consideration.id,
                question_slug=question.slug,
            )
            consideration.answers.append(answer)
        else:
            answer.text = data

        db.session.add(consideration)
        db.session.commit()
        if question.next:
            return redirect(
                url_for(
                    "questions.question",
                    consideration_slug=consideration_slug,
                    stage=stage,
                    question_slug=question.next,
                )
            )

    return redirect(
        url_for("questions.index", consideration_slug=consideration.slug, stage=stage)
    )
