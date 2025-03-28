import os

import frontmatter
import requests
from flask.cli import AppGroup
from sqlalchemy.orm.attributes import flag_modified

from application.models import Question, QuestionType

consider_cli = AppGroup("consider")


def extract_values(d, result):
    for key, value in d.items():
        if isinstance(value, dict):
            extract_values(value, result)
        elif key in ["slug", "prev", "next", "default_slug"]:
            result.add(value)


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
                "planning-data-design",
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
                "planning-data-design",
                path,
            ]
        )
        print(
            "\n\nRestored the dump to the local database using pg_restore. You can ignore warnings from pg_restore."
        )

    print("Data loaded successfully")


@consider_cli.command("check-dataset-links")
def check_dataset_links():
    from flask import current_app

    PLATFORM_URL = current_app.config["PLATFORM_URL"]
    DATASET_EDITOR_URL = current_app.config["DATASET_EDITOR_URL"]

    from application.extensions import db
    from application.models import Consideration

    platform_base_url = "{PLATFORM_URL}/dataset/{name}"
    dataset_editor_base_url = "{DATASET_EDITOR_URL}/dataset/{name}"

    for consideration in db.session.query(Consideration).all():
        if consideration.datasets:
            for i, dataset in enumerate(consideration.datasets):
                if "github" not in dataset["schema_url"]:
                    continue
                url = dataset["schema_url"].replace("?plain=1", "")
                markdown_url = f"{url}?raw=1"
                markdown = requests.get(markdown_url, allow_redirects=True)
                try:
                    markdown.raise_for_status()
                    front = frontmatter.loads(markdown.text)
                    if dataset["label"] is None:
                        dataset["label"] = front["name"]
                        flag_modified(consideration, "datasets")

                    if dataset["platform_url"] is None:
                        platform_url = _get_url_if_found(
                            platform_base_url.format(
                                name=dataset["name"], PLATFORM_URL=PLATFORM_URL
                            )
                        )
                        if platform_url is not None:
                            dataset["platform_url"] = platform_url
                            flag_modified(consideration, "datasets")

                    if dataset["dataset_editor_url"] is None:
                        dataset_editor_url = _get_url_if_found(
                            dataset_editor_base_url.format(
                                name=dataset["name"],
                                DATASET_EDITOR_URL=DATASET_EDITOR_URL,
                            )
                        )
                        if dataset_editor_url is not None:
                            dataset["dataset_editor_url"] = dataset_editor_url
                            flag_modified(consideration, "datasets")

                    if db.session.is_modified(consideration):
                        consideration.datasets[i] = dataset
                    else:
                        print(f"No changes for {consideration.name} datasets")

                except requests.exceptions.HTTPError as e:
                    print(f"Error fetching {markdown_url}: {e}")
                except Exception as e:
                    print(f"Error parsing {markdown_url}: {e}")

            if db.session.is_modified(consideration):
                db.session.add(consideration)
                db.session.commit()
                print(f"Updated {consideration.name} datasets")


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


def _get_url_if_found(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return url
    except requests.exceptions.HTTPError:
        return None
