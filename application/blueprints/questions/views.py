from flask import Blueprint, redirect, render_template, url_for

from application.blueprints.questions.forms import (
    ExistingDataForm,
    InputForm,
    LifecycleStagesForm,
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

    questions = (
        Question.query.filter(Question.stage == stage).order_by(Question.order).all()
    )

    return render_template(
        "questions/set.html",
        stage=stage,
        consideration=consideration,
        questions=questions,
        starting_question=next(iter(questions)),
    )


structured_data_forms = {
    "ExistingDataForm": ExistingDataForm,
    "LifecycleStagesForm": LifecycleStagesForm,
}


@questions.get("/<question_slug>")
def question(consideration_slug, stage, question_slug):
    from flask import request

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
            form.input.data = answer.answer["text"] if answer else None
            template = "questions/input.html"
        case QuestionType.TEXTAREA:
            form = TextareaForm(label=label)
            template = "questions/textarea.html"
            form.input.data = answer.answer["text"] if answer else None
        case QuestionType.CHOOSE_ONE_FROM_LIST:
            form = SingleChoiceForm(label=label)
            form.choice.choices = [(choice, choice) for choice in question.choices]
            form.choice.data = answer.answer["choice"] if answer else None
            template = "questions/single-choice.html"
        case QuestionType.CHOOSE_ONE_FROM_LIST_OTHER:
            form = SingleChoiceFormOther(label=label)
            form.choice.choices = [(choice, choice) for choice in question.choices]
            form.choice.data = answer.answer["choice"] if answer else None
            if (
                answer
                and answer.answer.get("choice") is not None
                and answer.answer.get("choice").lower() == "other"
            ):
                form.other.data = answer.answer["text"]
            template = "questions/single-choice.html"
        case QuestionType.ADD_TO_A_LIST:
            form = structured_data_forms[question.python_form]()
            template = "questions/add-to-a-list.html"
            print(form)
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
        next=request.args.get("next"),
    )


@questions.post("/<question_slug>")
def save_answer(consideration_slug, stage, question_slug):
    from flask import request

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
        case QuestionType.TEXTAREA:
            form = TextareaForm()
        case QuestionType.CHOOSE_ONE_FROM_LIST:
            form = SingleChoiceForm()
        case QuestionType.CHOOSE_ONE_FROM_LIST_OTHER:
            form = SingleChoiceFormOther()

    if form.is_submitted():

        match question.question_type:
            case QuestionType.INPUT:
                if form.input.data:
                    data = {"text": form.input.data}
                else:
                    data = None
            case QuestionType.TEXTAREA:
                if form.input.data:
                    data = {"text": form.input.data}
                else:
                    data = None
            case QuestionType.CHOOSE_ONE_FROM_LIST:
                if form.choice.data:
                    data = {"choice": form.choice.data}
                else:
                    data = None
            case QuestionType.CHOOSE_ONE_FROM_LIST_OTHER:
                if form.choice.data:
                    data = {"choice": form.choice.data}
                else:
                    data = None
                if data is not None and form.choice.data == "Other":
                    if form.other.data:
                        data["text"] = form.other.data
                    else:
                        data = None
            case _:
                data = None

        if data:
            answer = Answer.query.filter(
                Answer.consideration_id == consideration.id,
                Answer.question_slug == question.slug,
            ).one_or_none()

            if answer is None:
                answer = Answer(
                    answer=data,
                    consideration_id=consideration.id,
                    question_slug=question.slug,
                )
                consideration.answers.append(answer)
            else:
                answer.answer = data

            db.session.add(consideration)
            db.session.commit()

        else:
            answer = Answer.query.filter(
                Answer.consideration_id == consideration.id,
                Answer.question_slug == question.slug,
            ).one_or_none()
            if answer:
                db.session.delete(answer)
                db.session.commit()

        if question.next and request.args.get("next") is not None:
            question_slug = question.next.get("slug", None)
            if question.next["type"] == "condition":
                # In thef future, we might have multiple conditions to look through
                condition = question.next["conditions"][0]
                question_slug = question.next["default_slug"]
                if answer.answer["choice"] == condition["value"]:
                    question_slug = condition["slug"]

            return redirect(
                url_for(
                    "questions.question",
                    consideration_slug=consideration_slug,
                    stage=stage,
                    question_slug=question_slug,
                    next=True,
                )
            )

    return redirect(
        url_for("questions.index", consideration_slug=consideration.slug, stage=stage)
    )
