from flask import Blueprint, abort, jsonify, redirect, render_template, request, url_for

from application.blueprints.tags.forms import AddTagForm, TagForm
from application.extensions import db
from application.models import Consideration, Tag
from application.utils import login_required

tags = Blueprint(
    "tags",
    __name__,
    url_prefix="/admin",
)


@tags.route("/tags")
@tags.route("/")
@login_required
def index():
    tags = Tag.query.order_by(Tag.name).all()
    return render_template("tags/index.html", tags=tags)


@tags.route("/tags/add", methods=["GET", "POST"])
@login_required
def add():
    form = TagForm()
    action_url = url_for("tags.add")
    action_text = "Add tag"
    if form.validate_on_submit():
        tag = Tag(name=form.name.data.lower())
        db.session.add(tag)
        db.session.commit()
        return redirect(url_for("tags.index"))
    return render_template(
        "tags/tag-form.html", form=form, action_url=action_url, action_text=action_text
    )


@tags.route("/<string:tag_id>/edit", methods=["GET", "POST"])
@login_required
def edit_tag(tag_id):
    tag = Tag.query.get(tag_id)
    if tag is None:
        abort(404)
    form = TagForm(obj=tag)
    action_url = url_for("tags.edit_tag", tag_id=tag_id)
    action_text = "Edit tag"
    if form.validate_on_submit():
        tag.name = form.name.data.lower()
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


@tags.get("/<string:tag_id>/delete")
@login_required
def delete(tag_id):
    tag = Tag.query.get(tag_id)
    if tag is None:
        abort(404)
    db.session.delete(tag)
    db.session.commit()
    return redirect(url_for("tags.index"))


@tags.route("/<string:consideration>/add", methods=["GET", "POST"])
@login_required
def add_tag_consideration(consideration):
    consideration = Consideration.query.filter(
        Consideration.slug == consideration
    ).one_or_none()
    if consideration is None:
        abort(404)

    form = AddTagForm()
    form.new_tag.choices = [
        (tag.id, tag.name) for tag in Tag.query.order_by(Tag.name).all()
    ]

    if form.validate_on_submit():
        tag_id = form.new_tag.data
        if tag_id:
            tag = Tag.query.get(tag_id)
            if tag not in consideration.tags:
                consideration.tags.append(tag)
        if db.session.is_modified(consideration):
            db.session.add(consideration)
            db.session.commit()
        return redirect(
            url_for("planning_consideration.consideration", slug=consideration.slug)
        )
    action_url = url_for("tags.add_tag_consideration", consideration=consideration.slug)
    return render_template(
        "tags/tag-consideration-form.html",
        form=form,
        consideration=consideration,
        action_url=action_url,
    )


@tags.get("/<string:consideration>/<string:tag_id>/remove")
@login_required
def remove_tag(consideration, tag_id):
    consideration = Consideration.query.filter(
        Consideration.slug == consideration
    ).one_or_none()
    if consideration is None:
        abort(404)
    tag = Tag.query.get(tag_id)
    if tag is None:
        abort(404)
    consideration.tags.remove(tag)
    db.session.add(consideration)
    db.session.commit()
    return redirect(
        url_for("planning_consideration.consideration", slug=consideration.slug)
    )


@tags.route("/tags/add-ajax", methods=["POST"])
@login_required
def ajax_add_tag():
    data = request.json
    name = data["name"].strip().lower()
    tag = Tag.query.filter(Tag.name == name).one_or_none()
    if tag is None:
        tag = Tag(name=name)
        db.session.add(tag)
        db.session.commit()
    result = {"status": "success", "tag": tag.to_dict()}
    return jsonify(result)
