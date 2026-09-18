import logging
from functools import wraps
from typing import Optional

from werkzeug.routing import BaseConverter

from application.models import Question, QuestionType, Stage

logger = logging.getLogger(__name__)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import current_app, redirect, request, session, url_for

        if current_app.config.get("AUTHENTICATION_ON", True):
            if session.get("user") is None:
                return redirect(url_for("auth.login", next=request.path))
        return f(*args, **kwargs)

    return decorated_function


class StageConverter(BaseConverter):
    def to_python(self, stage):
        stage = stage.upper()
        stage = stage.replace("-", "_")
        try:
            return Stage[stage]
        except KeyError:
            return stage

    def to_url(self, stage):
        stage = stage.name.lower()
        stage = stage.replace("_", "-")
        return stage


def true_false_to_bool(s):
    if isinstance(s, bool):
        return s
    return s.lower() == "true"


def to_boolean(s):
    if isinstance(s, bool):
        return s
    if s.lower() in ["true", "1", "yes", "y", "on"]:
        return True
    if s.lower() in ["false", "0", "no", "n", "off"]:
        return False
    raise False


def get_question_by_slug(slug, stage):
    return Question.query.filter(Question.stage == stage, Question.slug == slug).one_or_none()


def get_next_question_slug(question, answer):
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


def get_next_question(question, consideration, stage):
    answer = consideration.get_answer(question)
    next_question_slug = get_next_question_slug(question, answer)
    return Question.query.filter(
        Question.stage == stage, Question.slug == next_question_slug
    ).one_or_none()


def get_question_group(start_question, consideration, stage, stop=None):
    question_group = []
    question_group.append(start_question)

    current_question = start_question
    while current_question and current_question.next:
        # exit if at end of sub flow
        next_question = get_next_question(current_question, consideration, stage)
        if next_question.slug == stop:
            break

        if current_question.next["type"] == "condition":
            # this means we've entered a sub flow
            if current_question.next["default_slug"] != next_question.slug:
                nested_group = get_question_group(
                    next_question,
                    consideration,
                    stage,
                    stop=current_question.next["default_slug"],
                )
                setattr(current_question, "sub_questions", nested_group)
                # make sure nested questions aren't also included in main question group
                next_question = get_question_by_slug(
                    current_question.next["default_slug"], stage
                )
        question_group.append(next_question)
        current_question = next_question

    return question_group


def load_questions_into_db() -> Optional[str]:
    """
    Load/update questions in the database
    Returns error message if there was a problem, None if successful
    """
    from application.extensions import db
    from application.question_sets import questions

    try:
        logger.info("Starting questions load/update")

        for stage in questions.keys():
            logger.debug(f"Loading questions for {stage}")
            qs = questions[stage]

            for q_order, q in enumerate(qs):
                try:
                    slug = next(iter(q.keys()))
                    logger.debug(f"Processing question: {q_order} {slug}")

                    question = Question.query.filter(
                        Question.slug == slug
                    ).one_or_none()
                    if question is None:
                        logger.info(f"Creating new question: '{slug}'")
                        question = Question(slug=slug, stage=stage)

                    q_data = q[slug]
                    # Validate required fields
                    if "question" not in q_data or "type" not in q_data:
                        logger.error(f"Question {slug} missing required fields")
                        continue

                    # Update question attributes with error handling
                    try:
                        question.text = q_data["question"]
                        question.hint = q_data.get("hint")
                        question.python_form = q_data.get("form")
                        question.order = q_order
                        question.question_type = QuestionType(q_data["type"])
                        question.next = q_data.get("next")
                        question.previous = q_data.get("prev")
                        question.choices = q_data.get("choices")

                        db.session.add(question)
                        db.session.commit()

                    except Exception as e:
                        logger.error(f"Error updating question {slug}: {str(e)}")
                        db.session.rollback()
                        continue

                except Exception as e:
                    logger.error(
                        f"Error processing question at index {q_order}: {str(e)}"
                    )
                    continue

        logger.info("Questions loaded successfully")
        return None

    except Exception as e:
        error_msg = f"Failed to load questions: {str(e)}"
        logger.error(error_msg)
        return error_msg
