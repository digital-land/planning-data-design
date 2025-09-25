from flask import Blueprint, render_template
from application.models import Consideration

project = Blueprint("project", __name__)


@project.route("/project")
def index():
    return render_template("projects.html")


@project.route("/project/planning-applications")
def planning_applications():
    considerations = sorted(
        Consideration.query.all(),
        key=lambda c: c.name,
    )
    return render_template(
        "advisory-group.html",
        considerations=considerations,
    )

@project.route("/project/planning-applications/members")
def advisory_group_members():
    return render_template("advisory-group-members.html")


@project.route("/project/planning-applications/roadmap")
def advisory_group_roadmap():
    return render_template("advisory-group-roadmap.html")

@project.route("/project/planning-applications/weeknotes")
def advisory_group_weeknotes():
    return render_template("advisory-group-weeknotes.html")