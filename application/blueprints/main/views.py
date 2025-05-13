import datetime
import os
import csv

from flask import Blueprint, abort, jsonify, redirect, render_template, request, url_for

from application.models import Consideration, Performance, PerformanceModel, Stage

main = Blueprint("main", __name__)


@main.route("/")
def index():
    return render_template("index.html")


@main.route("/cookies")
def cookies():
    # Get the cookie preferences from the request cookies
    cookies_policy = request.cookies.get(
        "cookies_policy", '{"essential":true,"usage":false}'
    )
    return render_template("cookies.html", cookies_policy=cookies_policy)


@main.route("/advisory-group")
def advisory_group():
    return redirect(url_for("project.planning_applications"), code=301)

@main.route("/how-to-contribute-to-the-data-design-process")
def get_involved():
    path = "pages/how-to-contribute-to-the-data-design-process.md"
    page = "how-to-contribute-to-the-data-design-process"
    return render_template("pages/scaffold.html", path=path, page=page)


@main.route("/advisory-group/members")
def advisory_group_members():
    return redirect(url_for("project.advisory_group_members"), code=301)


@main.route("/advisory-group/timeline")
def advisory_group_timeline():
    return redirect(url_for("project.advisory_group_roadmap"), code=301)


@main.route("/what-we-are-working-on")
def what_we_are_working_on():

    # List of stages to filter
    active_stages = [
        Stage.RESEARCH,
        Stage.CO_DESIGN,
        Stage.TEST_AND_ITERATE,
    ]
    # ["Research", "Co-design", "Test and iterate", "Ready for go/no-go"]
    active_considerations = sorted(
        Consideration.query.filter(Consideration.stage.in_(active_stages)).all(),
        key=lambda c: c.name,
    )

    emerging_priorities = sorted(
        Consideration.query.filter(Consideration.prioritised).all(),
        key=lambda c: c.name,
    )

    return render_template(
        "what-we-are-working-on.html",
        active_considerations=active_considerations,
        emerging_priorities=emerging_priorities,
    )


@main.route("/stage-count")
def stage_count():

    considerations = Consideration.query.all()

    data = {"considerations": len(considerations), "stages": {}}

    for consideration in considerations:
        data["stages"].setdefault(
            consideration.stage.name,
            {"name": consideration.stage.value, "considerations": []},
        )
        data["stages"][consideration.stage.name]["considerations"].append(consideration)

    # size of bars based on largest count
    data["largest_count"] = max(
        [len(stage["considerations"]) for stage in data["stages"].values()]
    )
    # how many considerations are blocked
    data["blocked_count"] = len(
        [
            consideration
            for consideration in considerations
            if consideration.blocked_reason is not None
        ]
    )
    active_considerations = [
        len(stage["considerations"])
        for stage in data["stages"].values()
        if stage["name"]
        in [
            "Screen",
            "Research",
            "Co-design",
            "Test and iterate",
        ]
    ]
    data["active_count"] = sum(active_considerations)
    data["max_active"] = max(active_considerations)

    return render_template("stage-count.html", data=data)


def _flatten_list_of_lists(data):
    return sum(data, [])


def _augment_change_entry(consideration):
    for change in consideration.changes:
        change["consideration"] = consideration.name
    return consideration.changes


def _count_coverage(considerations, attr_name):
    return len(
        [
            consideration
            for consideration in considerations
            if getattr(consideration, attr_name) is not None
        ]
    )


@main.route("/progress-report")
def progress_report():

    considerations = Consideration.query.all()
    all_changes = _flatten_list_of_lists(
        [
            _augment_change_entry(consideration)
            for consideration in considerations
            if consideration.changes is not None
        ]
    )

    # Calculate the date one week ago for default range
    since = datetime.datetime.now() - datetime.timedelta(weeks=1)
    since_param = request.args.get("since")
    if since_param:
        since = datetime.datetime.strptime(since_param, "%Y-%m-%d")

    recent_changes = [
        change
        for change in all_changes
        if datetime.datetime.strptime(change["date"], "%Y-%m-%d") >= since
    ]

    data = {
        "total": len(considerations),
        "with": {
            "legislation": _count_coverage(considerations, "legislation"),
            "specification": _count_coverage(considerations, "specification"),
            "schemas": _count_coverage(considerations, "schemas"),
            "useful_links": _count_coverage(considerations, "useful_links"),
            "github_discussion": _count_coverage(
                considerations, "github_discussion_number"
            ),
        },
        "edits": {"total": len(all_changes), "recent": len(recent_changes)},
    }
    return render_template("progress.html", data=data, since=since)


@main.route("/performance")
def performance():
    current = Performance.query.order_by(Performance.date.desc()).first()
    if not current:
        abort(404)
    model = PerformanceModel.model_validate(current).model_dump()

    data = {"current": model}

    dates = {
        "week": datetime.timedelta(weeks=1),
        "month": datetime.timedelta(days=30),
        "quarter": datetime.timedelta(days=90),
        "year": datetime.timedelta(days=365),
    }

    for label, date in dates.items():
        ago = current.date - date
        previous = Performance.query.filter(Performance.date == ago).one_or_none()
        if previous is not None:
            previous_model = PerformanceModel.model_validate(previous).model_dump()
            data[f"last_{label}"] = previous_model
        else:
            data[f"last_{label}"] = "No data"
    return jsonify(data)


@main.route("/<string:page>")
def page(page):
    if not os.path.exists(f"application/templates/pages/{page}.md"):
        abort(404)
    path = f"pages/{page}.md"
    return render_template("pages/scaffold.html", path=path, page=page)


# This route sits here as the tags blueprint is registered under /admin/tags
# and this is the public-facing glossary of tags.
# It is not part of the tags blueprint to avoid confusion with admin functionality.
@main.route("/tags/glossary")
def glossary_of_tags():
    tags = csv.DictReader(open("data/glossary-of-tags.csv", encoding="utf-8"))
    tags = sorted(tags, key=lambda x: x["name"].lower())
    return render_template("tags/glossary.html", tags=tags)
