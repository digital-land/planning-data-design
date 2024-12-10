from flask import Blueprint, abort, redirect, render_template, url_for

from application.blueprints.tags.forms import AddTagForm, TagForm
from application.extensions import db
from application.models import Consideration, Tag

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
    action_text = "Add tag"
    if form.validate_on_submit():
        tag = Tag(name=form.name.data)
        db.session.add(tag)
        db.session.commit()
        return redirect(url_for("tags.index"))
    return render_template(
        "tags/tag-form.html", form=form, action_url=action_url, action_text=action_text
    )


@tags.route("/<string:tag_id>/edit", methods=["GET", "POST"])
def edit_tag(tag_id):
    tag = Tag.query.get(tag_id)
    if tag is None:
        abort(404)
    form = TagForm(obj=tag)
    action_url = url_for("tags.edit_tag", tag_id=tag_id)
    action_text = "Edit tag"
    if form.validate_on_submit():
        tag.name = form.name.data
        db.session.add(tag)
        db.session.commit()
        return redirect(url_for("tags.index"))
    return render_template(
        "tags/tag-form.html",
        tag=tag,
        form=form,
        action_url=action_url,
        action_text=action_text,
    )


@tags.route("/<string:consideration_id>/add", methods=["GET", "POST"])
def tag_consideration(consideration_id):
    consideration = Consideration.query.get(consideration_id)
    if consideration is None:
        abort(404)

    form = AddTagForm()
    form.tags.choices = [
        (tag.id, tag.name) for tag in Tag.query.order_by(Tag.name).all()
    ]

    if form.validate_on_submit():
        tag = Tag.query.get(form.tags.data)
        if tag not in consideration.tags:
            consideration.tags.append(tag)
            db.session.add(consideration)
            db.session.commit()
        return redirect(
            url_for("planning_consideration.consideration", slug=consideration.slug)
        )
    return render_template(
        "tags/tag-consideration-form.html",
        form=form,
        consideration=consideration,
    )


@tags.get("/<string:consideration_id>/<string:tag_id>/remove")
def remove_tag(consideration_id, tag_id):
    consideration = Consideration.query.get(consideration_id)
    tag = Tag.query.get(tag_id)
    if consideration is None or tag is None:
        abort(404)
    consideration.tags.remove(tag)
    db.session.add(consideration)
    db.session.commit()
    return redirect(
        url_for("planning_consideration.consideration", slug=consideration.slug)
    )
