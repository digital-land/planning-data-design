import csv
import os

import gspread
import pandas as pd
from flask.cli import AppGroup, load_dotenv

from application.extensions import db
from application.models import Consideration, FrequencyOfUpdates, Stage

consider_cli = AppGroup("consider")


@consider_cli.command("fetch-grid")
def fetch_grid():

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
                name = row["Concern"]
                description = row["Description"]
                stage = row["Stage"]
                synonyms = row["Also called"].split(",") if row["Also called"] else []
                frequency_of_updates = row["Frequency of data updates"]
                if stage != "":
                    stage = (
                        stage.strip()
                        .upper()
                        .replace(" ", "_")
                        .replace("-", "_")
                        .replace("/", "_")
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

                github_discssion_number = row["discussion-number"]

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

                consideration = Consideration()
                if name:
                    consideration.name = name
                if description:
                    consideration.description = description
                if stage:
                    consideration.stage = stage
                if synonyms:
                    consideration.synonyms = synonyms
                if frequency_of_updates:
                    frequency_of_updates = frequency_of_updates
                if github_discssion_number:
                    consideration.github_discssion_number = github_discssion_number
                if useful_links:
                    consideration.useful_links = useful_links

                db.session.add(consideration)
                db.session.commit()
