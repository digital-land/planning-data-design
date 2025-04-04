from flask import Blueprint, abort, redirect, render_template, request, session, url_for

from application.blueprints.questions.forms import (
    ChooseMulitpleForm,
    ExistingDataForm,
    InputForm,
    LifecycleStagesForm,
    SingleChoiceForm,
    SingleChoiceFormOther,
    TextareaForm,
)
from application.extensions import db
from application.forms import DeleteForm
from application.models import (
    Answer,
    ChangeLog,
    Consideration,
    Question,
    QuestionType,
    Stage,
)
from application.utils import login_required, true_false_to_bool

questions = Blueprint(
    "questions",
    __name__,
    url_prefix="/planning-consideration/<string:consideration_slug>/<stage:stage>",
)


STRUCTURED_DATA_FORMS = {
    "ExistingDataForm": ExistingDataForm,
    "LifecycleStagesForm": LifecycleStagesForm,
}


def _get_question_by_slug(slug, stage):
    return Question.query.filter(
        Question.stage == stage, Question.slug == slug
    ).one_or_none()


def _get_next_question(question, consideration, stage):
    answer = consideration.get_answer(question)
    next_question_slug = _get_next_question_slug(question, answer)
    return Question.query.filter(
        Question.stage == stage, Question.slug == next_question_slug
    ).one_or_none()


def _get_question_group(start_question, consideration, stage, stop=None):
    question_group = []
    question_group.append(start_question)

    current_question = start_question
    while current_question and current_question.next:
        # exit if at end of sub flow
        next_question = _get_next_question(current_question, consideration, stage)
        if next_question.slug == stop:
            break

        if current_question.next["type"] == "condition":
            # this means we've entered a sub flow
            if current_question.next["default_slug"] != next_question.slug:
                nested_group = _get_question_group(
                    next_question,
                    consideration,
                    stage,
                    stop=current_question.next["default_slug"],
                )
                setattr(current_question, "sub_questions", nested_group)
                # make sure nested questions aren't also included in main question group
                next_question = _get_question_by_slug(
                    current_question.next["default_slug"], stage
                )
        question_group.append(next_question)
        current_question = next_question

    return question_group


@questions.get("/")
def index(consideration_slug, stage):
    if not isinstance(stage, Stage):
        abort(404)

    consideration = Consideration.query.filter(
        Consideration.slug == consideration_slug
    ).one_or_404()

    start_question = (
        Question.query.filter(Question.stage == stage).order_by(Question.order).first()
    )

    questions_to_display = _get_question_group(start_question, consideration, stage)

    return render_template(
        "questions/set.html",
        stage=stage,
        stages=Stage,
        consideration=consideration,
        questions=questions_to_display,
        starting_question=start_question,
    )


@questions.get("/<question_slug>")
def question(consideration_slug, stage, question_slug):
    if not isinstance(stage, Stage):
        abort(404)

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

    label = question.format(consideration.name)
    answer = consideration.get_answer(question)
    list_items = []
    if answer:
        list_items = answer.answer_list if answer.answer_list else []

    form, template = _get_form_and_template(question, label, answer)

    if form is None:
        return redirect(
            url_for(
                "questions.index",
                consideration_slug=consideration_slug,
                stage=stage,
            )
        )
    else:

        return render_template(
            template,
            consideration=consideration,
            form=form,
            question=question,
            stage=stage,
            next=request.args.get("next"),
            label=label,
            list_items=list_items,
        )


@questions.post("/<question_slug>")
@login_required
def save_answer(consideration_slug, stage, question_slug):
    if not isinstance(stage, Stage):
        abort(404)

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

    form = _get_form(question)

    if form.is_submitted():
        data = _get_form_data(question, form)
        if data:
            answer = Answer.query.filter(
                Answer.consideration_id == consideration.id,
                Answer.question_slug == question.slug,
            ).one_or_none()

            if answer is None:
                answer = Answer(
                    consideration_id=consideration.id,
                    question_slug=question.slug,
                )
                consideration.answers.append(answer)
            current_answer = answer.answer
            if question.question_type == QuestionType.ADD_TO_A_LIST:
                answer.answer_list = data
            else:
                answer.answer = data
            question_text = question.text.format(name=consideration.name)
            user = session.get("user", "unknown user")

            change_log = ChangeLog(
                field=question_text,
                change={"from": current_answer, "to": data},
                user=user,
            )
            if consideration.change_log is None:
                consideration.change_log = []
            consideration.change_log.append(change_log)

            db.session.add(answer)
            db.session.add(consideration)
            db.session.commit()
        else:
            answer = None

        if request.form.get("submit_button") == "add-another":
            return redirect(
                url_for(
                    "questions.add_to_list",
                    consideration_slug=consideration_slug,
                    stage=stage,
                    question_slug=question_slug,
                    next=request.args.get("next"),
                )
            )

        if question.next and (
            request.args.get("next") is not None
            or request.form.get("submit_button") == "next"
        ):
            question_slug = _get_next_question_slug(question, answer)
            if question_slug is not None:
                return redirect(
                    url_for(
                        "questions.question",
                        consideration_slug=consideration_slug,
                        stage=stage,
                        question_slug=question_slug,
                        next=(
                            None
                            if request.form.get("submit_button") == "next"
                            else True
                        ),
                    )
                )

    return redirect(
        url_for("questions.index", consideration_slug=consideration.slug, stage=stage)
    )


@questions.route("/<question_slug>/add-to-list", methods=["GET", "POST"])
@login_required
def add_to_list(consideration_slug, stage, question_slug):
    if not isinstance(stage, Stage):
        abort(404)

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

    answer = consideration.get_answer(question)
    if answer is None:
        answer = Answer(consideration_id=consideration.id, question_slug=question.slug)
        consideration.answers.append(answer)
    list_items = answer.answer_list if answer.answer_list else []
    form = STRUCTURED_DATA_FORMS[question.python_form]()
    form.position.data = len(list_items)
    template = "questions/add-to-a-list.html"

    if form.validate_on_submit():
        data = _get_form_data(question, form)
        if not data:
            return redirect(
                url_for(
                    "questions.index",
                    consideration_slug=consideration_slug,
                    stage=stage,
                )
            )
        else:
            previous_answers = answer.answer_list.copy() if answer.answer_list else None
            user = session.get("user", "unknown user")

            for item in data:
                answer.add_to_list(item)
                question_text = question.text.format(name=consideration.name)
                change_log = ChangeLog(
                    field=question_text,
                    change={"from": previous_answers, "to": answer.answer_list},
                    user=user,
                )
                if consideration.change_log is None:
                    consideration.change_log = []
                consideration.change_log.append(change_log)

            db.session.add(consideration)
            db.session.add(answer)
            db.session.commit()

        if request.form.get("submit_button") == "add-another":
            return redirect(
                url_for(
                    "questions.add_to_list",
                    consideration_slug=consideration_slug,
                    stage=stage,
                    question_slug=question_slug,
                    next=request.args.get("next"),
                )
            )

        if question.next and (
            request.args.get("next") is not None
            or request.form.get("submit_button") == "next"
        ):
            question_slug = _get_next_question_slug(question, answer)
            if question_slug is not None:
                return redirect(
                    url_for(
                        "questions.question",
                        consideration_slug=consideration_slug,
                        stage=stage,
                        question_slug=question_slug,
                        next=(
                            None
                            if request.form.get("submit_button") == "next"
                            else True
                        ),
                    )
                )
        return redirect(
            url_for(
                "questions.index", consideration_slug=consideration_slug, stage=stage
            )
        )

    return render_template(
        template,
        consideration=consideration,
        form=form,
        question=question,
        stage=stage,
        next=request.args.get("next"),
        list_items=list_items,
    )


@questions.route(
    "/<question_slug>/delete-from-list/<int:position>", methods=["GET", "POST"]
)
@login_required
def delete_answer(consideration_slug, stage, question_slug, position):
    if not isinstance(stage, Stage):
        abort(404)

    consideration = Consideration.query.filter(
        Consideration.slug == consideration_slug
    ).one_or_404()

    form = DeleteForm()

    if form.validate_on_submit():
        if true_false_to_bool(form.confirm.data):
            question = Question.query.filter(
                Question.stage == stage, Question.slug == question_slug
            ).one_or_none()

            if question is None:
                return redirect(
                    url_for(
                        "questions.add_to_list",
                        consideration_slug=consideration_slug,
                        stage=stage,
                        question_slug=question_slug,
                    )
                )

            answer = consideration.get_answer(question)
            if answer is not None and answer.answer_list:
                del answer.answer_list[position]
                for i, item in enumerate(answer.answer_list):
                    item["position"] = i
                db.session.add(answer)
                db.session.commit()

        return redirect(
            url_for(
                "questions.add_to_list",
                consideration_slug=consideration_slug,
                stage=stage,
                question_slug=question_slug,
            )
        )

    return render_template(
        "delete.html",
        caption="Delete answer",
        consideration=consideration,
        to_delete=f"answer {position + 1} from list",
        form=form,
        cancel_link=url_for(
            "questions.add_to_list",
            consideration_slug=consideration_slug,
            stage=stage,
            question_slug=question_slug,
        ),
    )


@questions.route("/<question_slug>/edit-answer/<int:position>", methods=["GET", "POST"])
@login_required
def edit_answer(consideration_slug, stage, question_slug, position):
    if not isinstance(stage, Stage):
        abort(404)

    consideration = Consideration.query.filter(
        Consideration.slug == consideration_slug
    ).one_or_404()

    question = Question.query.filter(
        Question.stage == stage, Question.slug == question_slug
    ).one_or_404()

    answer = consideration.get_answer(question)
    if answer is None or not answer.answer_list or len(answer.answer_list) <= position:
        abort(404)
    else:
        answer_item = answer.answer_list[position]
        form = STRUCTURED_DATA_FORMS[question.python_form](data=answer_item)

    if form.validate_on_submit():
        current_answer = answer.answer_list[position]
        answer.update_list(position, form.data)
        question_text = question.text.format(name=consideration.name)
        user = session.get("user", "unknown user")

        change_log = ChangeLog(
            field=question_text,
            change={"from": current_answer, "to": form.data},
            user=user,
        )
        if consideration.change_log is None:
            consideration.change_log = []
        consideration.change_log.append(change_log)

        db.session.add(answer)
        db.session.add(consideration)
        db.session.commit()

        return redirect(
            url_for(
                "questions.index", consideration_slug=consideration_slug, stage=stage
            )
        )

    return render_template(
        "questions/add-to-a-list.html",
        consideration=consideration,
        form=form,
        question=question,
        stage=stage,
        position=position,
        edit_single=True,
    )


def _populate_form(form, data):
    for d in data:
        for field in form:
            if field.name in d:
                field.data = d[field.name]


def _get_form_and_template(question, label, answer):
    form, template = None, None
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
        case QuestionType.CHOOSE_MULTIPLE_FROM_LIST:
            form = ChooseMulitpleForm(label=label)
            form.choice.choices = [(choice, choice) for choice in question.choices]
            form.choice.data = answer.answer["choice"].split(";") if answer else []
            template = "questions/multi-select.html"
        case QuestionType.ADD_TO_A_LIST:
            print(answer)
            form = STRUCTURED_DATA_FORMS[question.python_form]()
            template = "questions/add-to-a-list.html"
            if answer is not None and answer.answer_list:
                _populate_form(form, answer.answer_list)

    return form, template


def _get_form(question):
    form = None
    match question.question_type:
        case QuestionType.INPUT:
            form = InputForm()
        case QuestionType.TEXTAREA:
            form = TextareaForm()
        case QuestionType.CHOOSE_ONE_FROM_LIST:
            form = SingleChoiceForm()
        case QuestionType.CHOOSE_ONE_FROM_LIST_OTHER:
            form = SingleChoiceFormOther()
        case QuestionType.CHOOSE_MULTIPLE_FROM_LIST:
            form = ChooseMulitpleForm()
        case QuestionType.ADD_TO_A_LIST:
            form = STRUCTURED_DATA_FORMS[question.python_form]()
    return form


def _get_form_data(question, form):
    data = None
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
        case QuestionType.CHOOSE_MULTIPLE_FROM_LIST:
            if form.choice.data:
                data = {"choice": ";".join(form.choice.data)}
            else:
                data = None
        case QuestionType.ADD_TO_A_LIST:
            if any([key != "position" and val != "" for key, val in form.data.items()]):
                data = [form.data]
    return data


def _get_next_question_slug(question, answer):
    question_slug = question.next.get("slug", None)
    if question_slug is not None:
        return question_slug
    if answer is None:
        if question.next.get("default_slug") is not None:
            return question.next["default_slug"]
        else:
            return None
    if (
        question.next.get("type", None) is not None
        and question.next.get("type") == "condition"
    ):
        for condition in question.next["conditions"]:
            if (
                answer.answer["choice"] == condition["value"]
                and condition.get("slug") is not None
            ):
                return condition["slug"]
        else:
            if question.next.get("default_slug") is not None:
                return question.next["default_slug"]
    return None
