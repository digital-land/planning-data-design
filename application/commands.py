import frontmatter
import requests
from flask.cli import AppGroup
from sqlalchemy.orm.attributes import flag_modified

consider_cli = AppGroup("consider")


def extract_values(d, result):
    for key, value in d.items():
        if isinstance(value, dict):
            extract_values(value, result)
        elif key in ["slug", "prev", "next", "default_slug"]:
            result.add(value)


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
                        platform_url = _set_url_if_found(
                            platform_base_url.format(
                                name=dataset["name"], PLATFORM_URL=PLATFORM_URL
                            )
                        )
                        if platform_url is not None:
                            dataset["platform_url"] = platform_url
                            flag_modified(consideration, "datasets")

                    if dataset["dataset_editor_url"] is None:
                        dataset_editor_url = _set_url_if_found(
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


def _set_url_if_found(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return url
    except requests.exceptions.HTTPError:
        return None
