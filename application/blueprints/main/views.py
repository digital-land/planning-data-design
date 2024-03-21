from flask import Blueprint, redirect, render_template, request, url_for

from application.blueprints.main.forms import (
    ExpectedSizeForm,
    LinkForm,
    PriorityForm,
    PublicForm,
    SpecificationForm,
    StageForm,
    SynonymForm,
)
from application.extensions import db
from application.forms import ConsiderationForm
from application.models import Consideration, Stage

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


@main.route("/")
def index():
    stage_filter = None
    legislation_param = None
    stage_param = request.args.get("stage")
    legislation_param = request.args.get("legislation")

    if stage_param:
        stage = Stage(stage_param)
        stage_filter = stage_param
        considerations = (
            Consideration.query.filter_by(stage=stage)
            .order_by(Consideration.name.asc())
            .all()
        )
    else:
        considerations = Consideration.query.order_by(Consideration.name.asc()).all()

    # this is a temporary filter so not combining for now
    if legislation_param:
        filter_query = Consideration.legislation.is_(None)
        if legislation_param == "recorded":
            filter_query = Consideration.legislation.isnot(None)
        considerations = Consideration.query.filter(filter_query).all()

    return render_template(
        "index.html",
        considerations=considerations,
        stages=Stage,
        stage_filter=stage_filter,
        legislation_filter=legislation_param,
    )


@main.route("/planning-consideration/<slug>")
def consideration(slug):
    consideration = Consideration.query.filter(Consideration.slug == slug).first()
    return render_template("consideration.html", consideration=consideration)


@main.route("/planning-consideration/add", methods=["GET", "POST"])
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


@main.route(
    "/planning-consideration/<slug>/edit-specification", methods=["GET", "POST"]
)
def edit_specification(slug):
    consideration = Consideration.query.filter(Consideration.slug == slug).first()
    form = SpecificationForm(obj=consideration)

    if form.validate_on_submit():
        # handle form submission
        # redirect back to consideration page
        pass

    page = {"title": "Specification URL"}

    return render_template(
        "questiontypes/input.html",
        consideration=consideration,
        form=form,
        mode="edit",
        page=page,
    )


@main.route(
    "/planning-consideration/<slug>/edit-estimated-size", methods=["GET", "POST"]
)
def edit_estimated_size(slug):
    consideration = Consideration.query.filter(Consideration.slug == slug).first()
    form = ExpectedSizeForm(obj=consideration)

    if form.validate_on_submit():
        # handle form submission
        # redirect back to consideration page
        pass

    page = {"title": "Expected number of records"}

    return render_template(
        "questiontypes/input.html",
        consideration=consideration,
        form=form,
        mode="edit",
        page=page,
    )


@main.route("/planning-consideration/<slug>/add-synonym", methods=["GET", "POST"])
def add_synonym(slug):
    consideration = Consideration.query.filter(Consideration.slug == slug).first()
    form = SynonymForm(obj=consideration)

    if form.validate_on_submit():
        # handle form submission
        # To Do: check for duplicates
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
def stage(slug):
    consideration = Consideration.query.filter(Consideration.slug == slug).first()
    form = StageForm()

    if form.validate_on_submit():
        # handle form submission
        consideration.stage = Stage(form.stage.data)
        # To Do: record who changed it and the date
        db.session.add(consideration)
        db.session.commit()
        return redirect(url_for("main.consideration", slug=slug))

    form.stage.data = consideration.stage.value

    page = {"title": "Update stage", "submit_text": "Update"}

    return render_template(
        "questiontypes/input.html", consideration=consideration, form=form, page=page
    )


@main.route("/planning-consideration/<slug>/add-useful-link", methods=["GET", "POST"])
def add_useful_link(slug):
    consideration = Consideration.query.filter(Consideration.slug == slug).first()
    form = LinkForm()

    if form.validate_on_submit():
        # handle form submission
        current_links = []
        if consideration.useful_links is not None:
            current_links = [
                _link["link_url"]
                for _link in consideration.useful_links
                if consideration.useful_links
            ]
        if form.link_url.data not in current_links:
            # Adam - I could only get this to work if I create a new list rather than editing the existing list
            # existing list. Is that the right thing to do?
            _link = {"link_url": form.link_url.data, "link_text": form.link_text.data}
            links = (
                list(consideration.useful_links)
                if consideration.useful_links is not None
                else []
            )
            links.append(_link)
            consideration.useful_links = links
            db.session.add(consideration)
            db.session.commit()
            return redirect(url_for("main.consideration", slug=slug))

    page = {"title": "Add useful link", "submit_text": "Save link"}

    return render_template(
        "questiontypes/input.html", consideration=consideration, form=form, page=page
    )
