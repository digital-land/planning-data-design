import datetime

from flask import Blueprint, jsonify, render_template, request
from sqlalchemy import func

from application.extensions import db
from application.models import Consideration, Stage

main = Blueprint("main", __name__)


@main.route("/")
def index():
    return render_template("index.html")


@main.route("/data-design-process")
def data_design_process():
    return render_template("data-design-process.html")


@main.route("/how-to-contribute")
def how_to_contribute():
    return render_template("how-to-contribute.html")


@main.route("/what-we-are-working-on")
def what_we_are_working_on():

    # List of stages to filter
    active_stages = [
        Stage.RESEARCH,
        Stage.CO_DESIGN,
        Stage.TEST_AND_ITERATE,
        Stage.READY_FOR_GO_NO_GO,
    ]
    # ["Research", "Co-design", "Test and iterate", "Ready for go/no-go"]
    active_considerations = Consideration.query.filter(
        Consideration.stage.in_(active_stages)
    ).all()

    emerging_priorities = Consideration.query.filter(Consideration.prioritised).all()

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
            "Ready for go/no-go",
            "Prepared for platform",
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

    performance = {}

    result = (
        db.session.query(Consideration.stage, func.count())
        .group_by(Consideration.stage)
        .all()
    )
    considerations_by_stage = {stage.value: count for stage, count in result}
    performance["considerations_by_stage"] = considerations_by_stage

    # default time frame to the last week if not specified
    # in query
    timeframe = request.args.get("timeframe", "week")

    now = datetime.datetime.today()
    if timeframe == "week":
        start_date = now - datetime.timedelta(weeks=1)
    elif timeframe == "month":
        start_date = now - datetime.timedelta(days=30)
    elif timeframe == "quarter":
        start_date = now - datetime.timedelta(days=90)
    elif timeframe == "year":
        start_date = now - datetime.timedelta(days=365)
    else:
        return jsonify({"error": "Invalid timeframe"}), 400

    considerations_added = (
        db.session.query(func.count(Consideration.id))
        .filter(Consideration.created >= start_date)
        .scalar()
    )

    since = start_date.strftime("%Y-%m-%d")

    performance["considerations_added"] = {
        "timeframe": timeframe,
        "number": considerations_added,
        "since": since,
    }

    blocked_considerations = (
        db.session.query(func.count(Consideration.id))
        .filter(Consideration.blocked_reason.isnot(None))
        .scalar()
    )

    performance["blocked_considerations"] = blocked_considerations

    considerations_with_changes = (
        db.session.query(Consideration).filter(Consideration.changes.is_not(None)).all()
    )
    considerations_archived = sum(
        1
        for consideration in considerations_with_changes
        if any(
            change.get("to") == "Archived"
            and datetime.datetime.strptime(change.get("date"), "%Y-%m-%d") >= start_date
            for change in consideration.changes
        )
    )

    performance["considerations_archived"] = {
        "timeframe": timeframe,
        "number": considerations_archived,
        "since": since,
    }

    return jsonify(performance)
