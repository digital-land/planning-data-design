import datetime

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from markupsafe import Markup

from application.blueprints.main.forms import (
    DeleteForm,
    ExpectedSizeForm,
    FrequencyForm,
    LinkForm,
    PriorityForm,
    PublicForm,
    StageForm,
    SynonymForm,
)
from application.extensions import db
from application.forms import ConsiderationForm
from application.models import (
    Consideration,
    ConsiderationModel,
    FrequencyOfUpdates,
    Stage,
)
from application.utils import login_required

main = Blueprint("main", __name__)


def true_false_to_bool(s):
    return s.lower() == "true"


def _update_basic_consideration_attrs(consideration, form):
    # if a new consideration is needed
    if consideration is None:
        consideration = Consideration()
        consideration.stage = Stage("Backlog")
        is_new = True

    # set attributes
    consideration.name = form.name.data
    consideration.github_discussion_number = form.github_discussion_number.data
    consideration.description = form.description.data

    if is_new:
        consideration.set_slug()

    return consideration


def _update_link(consideration, attr_name, form):
    _link = {}
    _link["link_text"] = form.link_text.data
    _link["link_url"] = form.link_url.data
    setattr(consideration, attr_name, _link)
    db.session.add(consideration)
    db.session.commit()


def _extract_changes_of_type(consideration, attr_name):
    if consideration.changes is None:
        return None
    return [
        change
        for change in consideration.changes
        if attr_name in change["changes"].keys()
    ]


@main.route("/")
def index():
    return render_template("index.html")


@main.route("/planning-consideration")
def considerations():

    stage_param = request.args.get("stage")
    public_only = False if session.get("user") else True
    if public_only:
        query = Consideration.query.filter(Consideration.public == public_only)
    else:
        query = Consideration.query

    if stage_param:
        stage = Stage(stage_param)
        query = query.filter(Consideration.stage == stage)

    legislation_param = request.args.get("legislation")
    if legislation_param:
        if legislation_param == "recorded":
            query = query.filter(Consideration.legislation.isnot(None))
        else:
            query = query.filter(Consideration.legislation.is_(None))

    considerations = (
        query.filter(Consideration.deleted_date.is_(None))
        .order_by(Consideration.name.asc())
        .all()
    )

    return render_template(
        "considerations.html",
        considerations=considerations,
        stages=Stage,
        stage_filter=stage.value if stage_param else None,
        legislation_filter=legislation_param,
    )


@main.route("/planning-consideration/<slug>")
def consideration(slug):
    consideration = Consideration.query.filter(Consideration.slug == slug).first()

    # handle rouge consideration slugs
    if consideration is None:
        message = Markup(
            (
                "<p>We don't recognise <span class='govuk-!-font-weight-bold'>"
                f"{slug}</span>, maybe the spelling is different.</p><p>Use our "
                "<a class='govuk-list' href='#filter-considerations-list'>search</a>"
                " to see if the planning consideration exists.</p>"
            )
        )
        flash(message)
        return redirect(url_for("main.considerations"))

    latest_change = None
    if consideration.changes is not None:
        change_dates = [change["date"] for change in consideration.changes]
        latest_change = max(change_dates)

    return render_template(
        "consideration.html",
        consideration=consideration,
        latest_change=latest_change,
    )


@main.route("/planning-consideration/add", methods=["GET", "POST"])
@login_required
def new():
    form = ConsiderationForm()

    if form.validate_on_submit():
        consideration = _update_basic_consideration_attrs(None, form)
        db.session.add(consideration)
        db.session.commit()
        return redirect(url_for("main.consideration", slug=consideration.slug))

    return render_template("consideration-form.html", form=form)


@main.route("/planning-consideration/<slug>/edit", methods=["GET", "POST"])
@login_required
def edit(slug):
    consideration = Consideration.query.filter(Consideration.slug == slug).first()
    form = ConsiderationForm(obj=consideration)

    if form.validate_on_submit():
        consideration.name = form.name.data
        consideration.github_discussion_number = form.github_discussion_number.data
        consideration.description = form.description.data
        db.session.add(consideration)
        db.session.commit()
        return redirect(url_for("main.consideration", slug=slug))

    return render_template(
        "consideration-form.html", consideration=consideration, form=form, mode="edit"
    )


@main.route("/planning-consideration/<slug>/delete", methods=["GET", "POST"])
@login_required
def delete(slug):
    consideration = Consideration.query.filter(Consideration.slug == slug).first()
    form = DeleteForm()

    if form.validate_on_submit():
        if true_false_to_bool(form.confirm.data):
            consideration.delete()
            return redirect(url_for("main.considerations"))
        return redirect(url_for("main.consideration", slug=slug))

    return render_template("delete.html", consideration=consideration, form=form)


@main.route(
    "/planning-consideration/<slug>/edit-specification", methods=["GET", "POST"]
)
@login_required
def edit_specification(slug):
    consideration = Consideration.query.filter(Consideration.slug == slug).first()
    form = LinkForm()

    if form.validate_on_submit():
        _update_link(consideration, "specification", form)
        return redirect(url_for("main.consideration", slug=slug))

    if consideration.specification is not None:
        form.link_text.data = consideration.specification["link_text"]
        form.link_url.data = consideration.specification["link_url"]

    page = {"title": "Specification URL"}

    return render_template(
        "questiontypes/input.html",
        consideration=consideration,
        form=form,
        mode="edit",
        page=page,
    )


@main.route("/planning-consideration/<slug>/add-schema", methods=["GET", "POST"])
@login_required
def add_schema(slug):
    consideration = Consideration.query.filter(Consideration.slug == slug).first()
    form = LinkForm()
    form.link_text.label.text = "Schema name"

    if form.validate_on_submit():
        link = {"link_url": form.link_url.data, "link_text": form.link_text.data}
        if consideration.schemas is None:
            consideration.schemas = []
        consideration.schemas.append(link)
        db.session.add(consideration)
        db.session.commit()
        return redirect(url_for("main.consideration", slug=slug))

    page = {"title": "Add new schema", "submit_text": "Save schema"}

    return render_template(
        "questiontypes/input.html", consideration=consideration, form=form, page=page
    )


@main.route(
    "/planning-consideration/<slug>/<attr_name>/<link_text>/delete",
    methods=["GET", "POST"],
)
@login_required
def delete_attr_link(slug, attr_name, link_text):
    consideration = Consideration.query.filter(Consideration.slug == slug).first()

    # find matches
    has_changed = False
    links = getattr(consideration, attr_name)
    for link in links:
        if link["link_text"] == link_text:
            links.remove(link)
            has_changed = True

    if has_changed:
        setattr(consideration, attr_name, links)
        db.session.add(consideration)
        db.session.commit()

    return redirect(url_for("main.consideration", slug=slug))


@main.route(
    "/planning-consideration/<slug>/edit-estimated-size", methods=["GET", "POST"]
)
@login_required
def edit_estimated_size(slug):
    consideration = Consideration.query.filter(Consideration.slug == slug).first()
    form = ExpectedSizeForm(obj=consideration)

    if form.validate_on_submit():
        consideration.expected_number_of_records = form.expected_number_of_records.data
        db.session.add(consideration)
        db.session.commit()
        return redirect(url_for("main.consideration", slug=slug))

    page = {"title": "Expected number of records"}

    return render_template(
        "questiontypes/input.html",
        consideration=consideration,
        form=form,
        mode="edit",
        page=page,
    )


@main.route("/planning-consideration/<slug>/add-synonym", methods=["GET", "POST"])
@login_required
def add_synonym(slug):
    consideration = Consideration.query.filter(Consideration.slug == slug).first()
    form = SynonymForm(obj=consideration)

    if form.validate_on_submit():
        if consideration.synonyms is None:
            consideration.synonyms = []
        synonym = form.synonym.data.strip()
        if synonym not in consideration.synonyms:
            consideration.synonyms.append(synonym)
        db.session.add(consideration)
        db.session.commit()
        return redirect(url_for("main.consideration", slug=slug))

    page = {"title": "Add synonym", "submit_text": "Save synonym"}

    return render_template(
        "questiontypes/input.html",
        consideration=consideration,
        form=form,
        mode="edit",
        page=page,
    )


@main.route(
    "/planning-consideration/<slug>/synonym/<synonym>/delete", methods=["GET", "POST"]
)
@login_required
def delete_synonym(slug, synonym):
    consideration = Consideration.query.filter(Consideration.slug == slug).first()
    consideration.synonyms.remove(synonym)
    db.session.add(consideration)
    db.session.commit()
    return redirect(url_for("main.consideration", slug=slug))


@main.route("/planning-consideration/<slug>/prioritised", methods=["GET", "POST"])
@login_required
def prioritised(slug):
    consideration = Consideration.query.filter(Consideration.slug == slug).first()
    form = PriorityForm(obj=consideration)

    if form.validate_on_submit():
        consideration.prioritised = true_false_to_bool(form.prioritised.data)
        db.session.add(consideration)
        db.session.commit()
        return redirect(url_for("main.consideration", slug=slug))

    page = {"title": "Set prioritisation", "submit_text": "Set prioritisation"}

    return render_template(
        "questiontypes/input.html", consideration=consideration, form=form, page=page
    )


@main.route("/planning-consideration/<slug>/public", methods=["GET", "POST"])
@login_required
def public(slug):
    consideration = Consideration.query.filter(Consideration.slug == slug).first()
    form = PublicForm(obj=consideration)

    if form.validate_on_submit():
        consideration.public = true_false_to_bool(form.public.data)
        db.session.add(consideration)
        db.session.commit()
        return redirect(url_for("main.consideration", slug=slug))

    page = {"title": "Set public or private", "submit_text": "Set"}

    return render_template(
        "questiontypes/input.html", consideration=consideration, form=form, page=page
    )


@main.route("/planning-consideration/<slug>/stage")
def stage(slug):
    consideration = Consideration.query.filter(Consideration.slug == slug).first()

    stage_changes = _extract_changes_of_type(consideration, "stage")
    return render_template(
        "stage.html", consideration=consideration, stage_changes=stage_changes
    )


@main.route("/planning-consideration/<slug>/stage/change", methods=["GET", "POST"])
@login_required
def change_stage(slug):
    consideration = Consideration.query.filter(Consideration.slug == slug).first()
    form = StageForm()

    if form.validate_on_submit():
        updated_stage = consideration.stage
        consideration.stage = Stage(form.stage.data)
        reason = {
            "reason": form.data["reason"],
            "date": datetime.datetime.today().strftime("%Y-%m-%d"),
            "user": session["user"]["name"],
            "changes": {
                "stage": {
                    "added": consideration.stage.value,
                    "deleted": updated_stage.value,
                },
            },
        }
        if consideration.changes is None:
            consideration.changes = []
        consideration.changes.append(reason)
        db.session.add(consideration)
        db.session.commit()
        return redirect(url_for("main.consideration", slug=slug))

    form.stage.data = consideration.stage.value

    page = {"title": "Update stage", "submit_text": "Update"}

    return render_template(
        "questiontypes/input.html", consideration=consideration, form=form, page=page
    )


@main.route("/planning-consideration/<slug>/edit-frequency", methods=["GET", "POST"])
@login_required
def frequency(slug):
    consideration = Consideration.query.filter(Consideration.slug == slug).first()
    form = FrequencyForm()

    if form.validate_on_submit():
        consideration.frequency_of_updates = FrequencyOfUpdates(form.frequency.data)
        db.session.add(consideration)
        db.session.commit()
        return redirect(url_for("main.consideration", slug=slug))

    form.frequency.data = (
        consideration.frequency_of_updates.value
        if consideration.frequency_of_updates
        else ""
    )

    page = {"title": "Edit expected frequency of updates", "submit_text": "Save"}

    return render_template(
        "questiontypes/input.html", consideration=consideration, form=form, page=page
    )


@main.route("/planning-consideration/<slug>/add-useful-link", methods=["GET", "POST"])
@login_required
def add_useful_link(slug):
    consideration = Consideration.query.filter(Consideration.slug == slug).first()
    form = LinkForm()

    if form.validate_on_submit():
        link = {"link_url": form.link_url.data, "link_text": form.link_text.data}
        if consideration.useful_links is None:
            consideration.useful_links = []
        consideration.useful_links.append(link)

        db.session.add(consideration)
        db.session.commit()
        return redirect(url_for("main.consideration", slug=slug))

    page = {"title": "Add useful link", "submit_text": "Save link"}

    return render_template(
        "questiontypes/input.html", consideration=consideration, form=form, page=page
    )


@main.route("/planning-consideration.json")
def considerations_json():
    considerations = Consideration.query.all()
    data = {
        "considerations": [
            ConsiderationModel.model_validate(c).model_dump()
            for c in considerations
            if c.public
        ]
    }
    return data


@main.route("/planning-consideration/<slug>/edit-legislation", methods=["GET", "POST"])
@login_required
def edit_legislation(slug):
    consideration = Consideration.query.filter(Consideration.slug == slug).first()
    form = LinkForm(url_required=False)

    if form.validate_on_submit():
        # handle submitted form
        _update_link(consideration, "legislation", form)
        return redirect(url_for("main.consideration", slug=slug))

    if consideration.legislation is not None:
        form.link_text.data = consideration.legislation["link_text"]
        form.link_url.data = consideration.legislation["link_url"]

    page = {"title": "Edit legislation", "submit_text": "Save"}

    return render_template(
        "questiontypes/input.html", consideration=consideration, form=form, page=page
    )


# Report pages
# ============


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

    data["largest_count"] = max(
        [len(stage["considerations"]) for stage in data["stages"].values()]
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
            "legislation": len(
                [
                    consideration
                    for consideration in considerations
                    if consideration.legislation is not None
                ]
            ),
            "specification": len(
                [
                    consideration
                    for consideration in considerations
                    if consideration.specification is not None
                ]
            ),
            "schemas": len(
                [
                    consideration
                    for consideration in considerations
                    if consideration.schemas is not None
                ]
            ),
            "useful_links": len(
                [
                    consideration
                    for consideration in considerations
                    if consideration.useful_links is not None
                ]
            ),
        },
        "edits": {"total": len(all_changes), "recent": len(recent_changes)},
    }
    return render_template("progress.html", data=data, since=since)
