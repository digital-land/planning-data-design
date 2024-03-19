from flask import Blueprint, render_template

from application.models import Consideration

main = Blueprint("main", __name__)


@main.route("/")
def index():
    considerations = Consideration.query.all()
    return render_template("index.html", considerations=considerations)


@main.route("/planning-consideration/<slug>")
def consideration(slug):
    consideration = Consideration.query.filter(Consideration.slug == slug).first()
    return render_template("consideration.html", consideration=consideration)
