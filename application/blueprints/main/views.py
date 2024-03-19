from flask import Blueprint, render_template

from application.forms import ConsiderationForm
from application.models import Consideration, Stage

main = Blueprint("main", __name__)


@main.route("/")
def index():
    considerations = Consideration.query.all()
    return render_template("index.html", considerations=considerations, stages=Stage)


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

    return render_template("new.html", form=form)
