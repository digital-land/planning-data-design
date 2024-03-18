from flask import Blueprint, render_template

from application.models import Consideration

main = Blueprint("main", __name__)


@main.route("/")
def index():
    considerations = Consideration.query.all()
    return render_template("index.html", considerations=considerations)
