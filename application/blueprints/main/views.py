import datetime

from flask import Blueprint, redirect, render_template, request, session, url_for

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
        considerations = query.order_by(Consideration.name.asc()).all()
    else:
        considerations = query.order_by(Consideration.name.asc()).all()

    legislation_param = request.args.get("legislation")
    if legislation_param:
        if legislation_param == "recorded":
            query = query.filter(Consideration.legislation.isnot(None))
        else:
            query = query.filter(Consideration.legislation.is_(None))

    considerations = query.all()

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
    return render_template("consideration.html", consideration=consideration)


@main.route("/planning-consideration/add", methods=["GET", "POST"])
@login_required
def new():
    form = ConsiderationForm()

    if form.validate_on_submit():
        # handle form submission
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
        # handle form submission
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
        # handle deleting consideration
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
        # handle form submission
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
    "/planning-consideration/<slug>/schema/<schema_name>/delete",
    methods=["GET", "POST"],
)
@login_required
def delete_schema(slug, schema_name):
    consideration = Consideration.query.filter(Consideration.slug == slug).first()

    # find matches
    has_changed = False
    for schema in consideration.schemas:
        if schema["link_text"] == schema_name:
            consideration.schemas.remove(schema)
            has_changed = True

    if has_changed:
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
        # handle form submission
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
        # handle form submission
        # To Do: check for duplicates
        # Adam - I could only get this to work if I create a new list rather than editing the existing list
        synonyms = list()
        synonyms = set([form.synonym.data] + consideration.synonyms)
        consideration.synonyms = synonyms
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


@main.route("/planning-consideration/<slug>/prioritised", methods=["GET", "POST"])
@login_required
def prioritised(slug):
    consideration = Consideration.query.filter(Consideration.slug == slug).first()
    form = PriorityForm(obj=consideration)

    if form.validate_on_submit():
        # handle form submission
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
        # handle form submission
        consideration.public = true_false_to_bool(form.public.data)
        db.session.add(consideration)
        db.session.commit()
        return redirect(url_for("main.consideration", slug=slug))

    page = {"title": "Set public or private", "submit_text": "Set"}

    return render_template(
        "questiontypes/input.html", consideration=consideration, form=form, page=page
    )


@main.route("/planning-consideration/<slug>/stage", methods=["GET", "POST"])
@login_required
def stage(slug):
    consideration = Consideration.query.filter(Consideration.slug == slug).first()
    form = StageForm()

    if form.validate_on_submit():
        consideration.stage = Stage(form.stage.data)
        reason = {
            "reason": form.data["reason"],
            "date": datetime.datetime.today().strftime("%Y-%m-%d"),
            "user": session["user"]["name"],
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
        # handle form submission
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
