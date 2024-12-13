from flask import Blueprint, abort, redirect, render_template, request, url_for

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
    if form.next_url.data is None:
        form.next_url.data = request.args.get("next_url")
    if form.validate_on_submit():
        tag = Tag(name=form.name.data)
        db.session.add(tag)
        db.session.commit()
        next_url = form.next_url.data
        if next_url:
            next_url = f"{next_url}?tag={tag.id}"
            return redirect(next_url)  # check the next_url is a valid
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


@tags.get("/<string:tag_id>/delete")
def delete(tag_id):
    tag = Tag.query.get(tag_id)
    if tag is None:
        abort(404)
    db.session.delete(tag)
    db.session.commit()
    return redirect(url_for("tags.index"))


@tags.route("/<string:consideration>/add", methods=["GET", "POST"])
def add_tag_consideration(consideration):
    consideration = Consideration.query.filter(
        Consideration.slug == consideration
    ).one_or_none()
    if consideration is None:
        abort(404)

    form = AddTagForm()
    form.tags.choices = [
        (tag.id, tag.name) for tag in Tag.query.order_by(Tag.name).all()
    ]
    if request.args.get("tag"):
        form.tags.data = request.args.get("tag")

    if form.validate_on_submit():
        tag_ids = form.tags.data.split(";")
        for tag_id in tag_ids:
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


@tags.route("/<string:consideration>/update", methods=["GET", "POST"])
def update_tag_consideration(consideration):
    consideration = Consideration.query.filter(
        Consideration.slug == consideration
    ).one_or_none()
    if consideration is None:
        abort(404)

    form = AddTagForm()

    if form.validate_on_submit():
        consideration.tags.clear()
        tag_ids = form.tags.data.split(";")
        for tag_id in tag_ids:
            if tag_id:
                tag = Tag.query.get(tag_id)
                consideration.tags.append(tag)
        if db.session.is_modified(consideration):
            db.session.add(consideration)
            db.session.commit()
        return redirect(
            url_for("planning_consideration.consideration", slug=consideration.slug)
        )
    action_url = url_for(
        "tags.update_tag_consideration", consideration=consideration.slug
    )

    existing_tags = ";".join([str(tag.id) for tag in consideration.tags])
    if request.args.get("tag"):
        existing_tags = f"{existing_tags};{request.args.get('tag')}"
    form.tags.data = existing_tags

    form.tags.choices = [
        (tag.id, tag.name) for tag in Tag.query.order_by(Tag.name).all()
    ]

    return render_template(
        "tags/tag-consideration-form.html",
        form=form,
        consideration=consideration,
        action_url=action_url,
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
