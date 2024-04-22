import os

from flask.cli import AppGroup

from application.models import Question, QuestionType

consider_cli = AppGroup("consider")


@consider_cli.command("load-data")
def load_data():
    import subprocess
    import sys
    import tempfile

    from flask import current_app

    # check heroku cli installed
    result = subprocess.run(["which", "heroku"], capture_output=True, text=True)

    if result.returncode == 1:
        print("Heroku CLI is not installed. Please install it and try again.")
        sys.exit(1)

    # check heroku login
    result = subprocess.run(["heroku", "whoami"], capture_output=True, text=True)

    if "Error: not logged in" in result.stderr:
        print("Please login to heroku using 'heroku login' and try again.")
        sys.exit(1)

    print("Starting load data into", current_app.config["SQLALCHEMY_DATABASE_URI"])
    if (
        input(
            "Completing process will overwrite your local database. Enter 'y' to continue, or anything else to exit. "
        )
        != "y"
    ):
        print("Exiting without making any changes")
        sys.exit(0)

    with tempfile.TemporaryDirectory() as tempdir:
        path = os.path.join(tempdir, "latest.dump")

        # get the latest dump from heroku
        result = subprocess.run(
            [
                "heroku",
                "pg:backups:download",
                "-a",
                "dluhc-planning-considerations",
                "-o",
                path,
            ]
        )

        if result.returncode != 0:
            print("Error downloading the backup")
            sys.exit(1)

        # restore the dump to the local database
        subprocess.run(
            [
                "pg_restore",
                "--verbose",
                "--clean",
                "--no-acl",
                "--no-owner",
                "-h",
                "localhost",
                "-d",
                "dluhc-planning-considerations",
                path,
            ]
        )
        print(
            "\n\nRestored the dump to the local database using pg_restore. You can ignore warnings from pg_restore."
        )

    print("Data loaded successfully")


@consider_cli.command("load-questions")
def load_questions():

    # how do we preserve order?

    from application.extensions import db
    from application.question_sets import questions

    print("\nLoading/updating questions")

    for stage in questions.keys():
        print("Loading questions for", stage)
        qs = questions[stage]
        for q_order, q in enumerate(qs):
            slug = next(iter(q.keys()))
            print(f"\t Loading question: {q_order} {slug}")
            question = Question.query.filter(Question.slug == slug).one_or_none()
            if question is None:
                print(f"\t\tCreating question: '{slug}'")
                question = Question(slug=slug, stage=stage)
            else:
                print(
                    f"\t\tReloading question {q_order}: '{slug}'. Any changes will be applied."
                )

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

    print("Questions loaded successfully")


def extract_values(d, result):
    for key, value in d.items():
        if isinstance(value, dict):
            extract_values(value, result)
        elif key in ["url", "prev", "next", "default_url"]:
            result.add(value)


@consider_cli.command("check-questions")
def check_questions():
    from application.question_sets import questions

    for stage in questions.keys():
        qs = questions[stage]
        slugs = set([next(iter(q.keys())) for q in qs])
        next_prev_slugs = set([])
        for q in qs:
            extract_values(q, next_prev_slugs)

        if not next_prev_slugs.issubset(slugs):
            print(f"{stage} failed check")
            print(f"{next_prev_slugs - slugs} not found in {stage}")
            print(f"Slugs {slugs}")
            print(f"Next/prev slugs {next_prev_slugs}\n")

        else:
            print(f"Next/prev/default slugs are valid for {stage}\n")
