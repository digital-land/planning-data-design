import csv
import os

import gspread
import pandas as pd
from flask.cli import AppGroup, load_dotenv

from application.extensions import db
from application.models import Consideration, FrequencyOfUpdates, Stage

consider_cli = AppGroup("consider")


def _fetch():
    load_dotenv()

    google_credentials = {
        "type": "service_account",
        "project_id": "data-standards-389209",
        "private_key_id": os.getenv("GOOGLE_PRIVATE_KEY_ID"),
        "private_key": os.getenv("GOOGLE_PRIVATE_KEY").replace("\\n", "\n"),
        "client_email": os.getenv("GOOGLE_CLIENT_EMAIL"),
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/"
        "data-standards-team-bot%40data-standards-389209.iam.gserviceaccount.com",
        "universe_domain": "googleapis.com",
    }

    gc = gspread.service_account_from_dict(google_credentials)

    spreadsheet = gc.open("The grid")
    worksheet = spreadsheet.worksheet("planning-concerns")

    data = worksheet.get_all_values()
    df = pd.DataFrame(data)

    # Remove the third row (index 2)
    df = df.drop(0)
    df = df.drop(2)

    df.to_csv("data/planning-concerns-backlog.csv", index=False, header=False)


@consider_cli.command("update-backlog")
def update_backlog():
    _fetch()
    backlog_file_path = "data/planning-concerns-backlog.csv"
    if os.path.exists(backlog_file_path):
        with open(backlog_file_path, "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                name = row["Concern"]
                consideration = Consideration.query.filter(
                    Consideration.name == name
                ).one_or_none()
                if consideration is None:
                    consideration = Consideration()
                set_fields(consideration, row)
                db.session.add(consideration)
                db.session.commit()


@consider_cli.command("fetch-grid")
def fetch_grid():
    _fetch()


@consider_cli.command("drop-backlog")
def drop_backlog():
    db.session.query(Consideration).delete()
    db.session.commit()


@consider_cli.command("load-backlog")
def load_backlog():

    backlog_file_path = "data/planning-concerns-backlog.csv"

    if os.path.exists(backlog_file_path):
        with open(backlog_file_path, "r") as file:
            reader = csv.DictReader(file)

            for row in reader:
                consideration = Consideration()
                set_fields(consideration, row)
                db.session.add(consideration)
                db.session.commit()


def set_fields(consideration, row):
    description = row["Description"]
    stage = row["Stage"]
    synonyms = row["Also called"].split(",") if row["Also called"] else []
    frequency_of_updates = row["Frequency of data updates"]
    if stage != "":
        stage = (
            stage.strip().upper().replace(" ", "_").replace("-", "_").replace("/", "_")
        )
        stage = Stage[stage]

    if frequency_of_updates != "":
        frequency_of_updates = (
            frequency_of_updates.strip()
            .upper()
            .replace(" ", "_")
            .replace("-", "_")
            .replace("/", "_")
        )
        frequency_of_updates = FrequencyOfUpdates[frequency_of_updates]

    github_discussion_number = row["discussion-number"]

    useful_links = []
    link_columns = [
        "National dataset documentation page",
        "URL of national dataset",
        "Fact sheet url",
    ]
    for link in link_columns:
        if row[link] != "":
            useful_links.append(
                {
                    "link_text": link,
                    "link_url": row[link],
                }
            )

    legistlation = row["Legislation"]

    if consideration.name is None:
        name = row["Concern"]
        consideration.name = name
        consideration.set_slug()
    if description:
        consideration.description = description
    if stage:
        consideration.stage = stage
    if synonyms:
        consideration.synonyms = synonyms
    if frequency_of_updates:
        frequency_of_updates = frequency_of_updates
    if github_discussion_number:
        consideration.github_discussion_number = github_discussion_number
    if useful_links:
        consideration.useful_links = useful_links
    if legistlation:
        consideration.legislation = {"link_text": legistlation, "link_url": None}

    return consideration


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
            "Completing process will overwrite your localdatabase. Enter 'y' to continue, or anything else to exit. "
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
