from flask import Blueprint, redirect, render_template, request, url_for

from application.blueprints.main.forms import LinkForm, SpecificationForm
from application.extensions import db
from application.forms import ConsiderationForm
from application.models import Consideration, Stage

main = Blueprint("main", __name__)


@main.route("/")
def index():
    stage_filter = None
    stage_param = request.args.get("stage")
    if stage_param:
        stage = Stage(stage_param)
        stage_filter = stage_param
        considerations = Consideration.query.filter_by(stage=stage).all()
    else:
        considerations = Consideration.query.all()

    return render_template(
        "index.html",
        considerations=considerations,
        stages=Stage,
        stage_filter=stage_filter,
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
        # redirect to page for the new consideration
        pass

    return render_template("consideration-form.html", form=form)


@main.route("/planning-consideration/<slug>/edit", methods=["GET", "POST"])
def edit(slug):
    consideration = Consideration.query.filter(Consideration.slug == slug).first()
    form = ConsiderationForm(obj=consideration)

    if form.validate_on_submit():
        # handle form submission
        # redirect back to consideration page
        pass

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
            links = list(consideration.useful_links)
            links.append(_link)
            consideration.useful_links = links
            db.session.add(consideration)
            db.session.commit()
            return redirect(url_for("main.consideration", slug=slug))

    page = {"title": "Add useful link", "submit_text": "Save link"}

    return render_template(
        "questiontypes/input.html", consideration=consideration, form=form, page=page
    )
