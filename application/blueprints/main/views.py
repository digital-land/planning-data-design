from flask import Blueprint, render_template, request

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
