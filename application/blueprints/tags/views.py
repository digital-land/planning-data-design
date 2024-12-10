from flask import Blueprint, abort, redirect, render_template, url_for

from application.blueprints.tags.forms import TagForm
from application.extensions import db
from application.models import Tag

tags = Blueprint(
    "tags",
    __name__,
    url_prefix="/tags",
)


@tags.route("/")
def index():
    tags = Tag.query.order_by(Tag.name).all()
    return render_template("tags/index.html", tags=tags)


@tags.route("/add", methods=["GET", "POST"])
def add():
    form = TagForm()
    action_url = url_for("tags.add")
    if form.validate_on_submit():
        tag = Tag(name=form.name.data)
        db.session.add(tag)
        db.session.commit()
        return redirect(url_for("tags.index"))
    return render_template("tags/tag-form.html", form=form, action_url=action_url)


@tags.route("/<string:tag_id>", methods=["GET", "POST"])
def tag(tag_id):
    tag = Tag.query.get(tag_id)
    if tag is None:
        abort(404)
    form = TagForm(obj=tag)
    action_url = url_for("tags.tag", tag_id=tag_id)
    if form.validate_on_submit():
        tag.name = form.name.data
        db.session.add(tag)
        db.session.commit()
        return redirect(url_for("tags.index"))
    return render_template(
        "tags/tag-form.html", tag=tag, form=form, action_url=action_url
    )
