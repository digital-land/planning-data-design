import pytest

from application.extensions import db
from application.factory import create_app
from application.models import Question, QuestionType


@pytest.fixture(scope="session")
def app():
    application = create_app("config.TestConfig")

    with application.app_context():
        db.create_all()

    yield application

    with application.app_context():
        db.drop_all()


@pytest.fixture(scope="session")
def client(app):
    return app.test_client()


@pytest.fixture(scope="session")
def questions(app):

    from application.extensions import db
    from application.question_sets import questions

    with app.app_context():
        for stage in questions.keys():
            qs = questions[stage]
            for q_order, q in enumerate(qs):
                slug = next(iter(q.keys()))
                question = Question.query.filter(Question.slug == slug).one_or_none()
                if question is None:
                    question = Question(slug=slug, stage=stage)

                q = q[slug]
                question.text = q["question"]
                question.hint = q.get("hint", None)
                question.python_form = q.get("form", None)
                question.order = q_order
                question.question_type = QuestionType(q["type"])
                question.next = q.get("next", None)
                question.previous = q.get("prev", None)
                question.choices = q.get("choices", None)

                db.session.add(question)
                db.session.commit()

    return app
