import csv
import datetime
import io
from enum import Enum
from urllib.parse import urlparse

from flask import (
    Blueprint,
    Response,
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from markupsafe import Markup
from slugify import slugify
from sqlalchemy import and_, or_

from application.blueprints.planning_consideration.forms import (
    BlockedForm,
    ConsiderationForm,
    DatasetForm,
    ExpectedSizeForm,
    FrequencyForm,
    LinkForm,
    NoteForm,
    OSDeclarationForm,
    PriorityForm,
    PublicForm,
    StageForm,
    SynonymForm,
)
from application.extensions import db
from application.forms import DeleteForm
from application.models import (
    Answer,
    ChangeLog,
    Consideration,
    ConsiderationModel,
    FrequencyOfUpdates,
    Note,
    OSDeclarationStatus,
    Stage,
    Tag,
)
from application.question_sets import publishing_organisations
from application.utils import login_required, true_false_to_bool

enum_map = {
    "frequency_of_updates": FrequencyOfUpdates,
}

planning_consideration = Blueprint(
    "planning_consideration",
    __name__,
    url_prefix="/planning-consideration",
)


def _create_or_update_consideration(form, attributes, is_new=False, consideration=None):

    if consideration is None:
        consideration = Consideration()
        consideration.stage = Stage("Backlog")

    for attribute in attributes:
        from_value = None
        to_value = None
        match attribute:
            case (
                "name"
                | "github_discussion_number"
                | "description"
                | "expected_number_of_records"
            ):
                column_type = consideration.get_column_type(attribute)
                if column_type.python_type == str:
                    data = form.data.get(attribute, "").strip()
                    if data and attribute == "name":
                        data = data[0].upper() + data[1:].lower()
                else:
                    data = form.data.get(attribute)
                if data != getattr(consideration, attribute) or not getattr(
                    consideration, attribute
                ):
                    from_value = getattr(consideration, attribute)
                    to_value = data
                    setattr(consideration, attribute, data)

            case (
                "public" | "is_local_land_charge" | "prioritised" | "is_local_plan_data"
            ):
                column_type = consideration.get_column_type(attribute)
                data = true_false_to_bool(form.data.get(attribute))
                if data != getattr(consideration, attribute) or not getattr(
                    consideration, attribute
                ):
                    from_value = getattr(consideration, attribute)
                    to_value = data
                    setattr(consideration, attribute, data)

            case "specification" | "legislation":
                data = {
                    "link_text": form.link_text.data,
                    "link_url": form.link_url.data,
                }
                if data != getattr(consideration, attribute) or not getattr(
                    consideration, attribute
                ):
                    from_value = getattr(consideration, attribute)
                    to_value = data
                    setattr(consideration, attribute, data)

            case "os_declaration":
                data = {
                    "status": form.status.data,
                    "further_information_url": form.further_information_url.data,
                }
                if data != getattr(consideration, attribute) or not getattr(
                    consideration, attribute
                ):
                    from_value = getattr(consideration, attribute)
                    to_value = data
                    setattr(consideration, attribute, data)

            case "useful_links":
                data = {
                    "link_text": form.link_text.data,
                    "link_url": form.link_url.data,
                }
                if getattr(consideration, attribute) is None:
                    setattr(consideration, attribute, [])
                if data not in getattr(consideration, attribute):
                    from_value = getattr(consideration, attribute).copy()
                    getattr(consideration, attribute).append(data)
                    to_value = getattr(consideration, attribute)

            case "dataset":
                field = f"{attribute}s"
                if getattr(consideration, field) is None:
                    setattr(consideration, field, [])

                dataset_schema_url = form.data.get(attribute)
                parsed_url = urlparse(dataset_schema_url)
                name = parsed_url.path.split("/")[-1].replace(".md", "")

                data = {
                    "name": name,
                    "label": None,
                    "schema_url": dataset_schema_url,
                    "platform_url": None,
                    "dataset_editor_url": None,
                }
                if data not in getattr(consideration, field):
                    from_value = getattr(consideration, field).copy()
                    getattr(consideration, field).append(data)
                    to_value = getattr(consideration, field)

            case "synonym":
                field = f"{attribute}s"
                if getattr(consideration, field) is None:
                    setattr(consideration, field, [])

                data = form.data.get(attribute).strip()
                if data not in getattr(consideration, field):
                    from_value = getattr(consideration, field).copy()
                    getattr(consideration, field).append(data)
                    to_value = getattr(consideration, field)

            case "frequency_of_updates":
                enum = enum_map.get(attribute)
                data = enum(form.data.get(attribute))
                if data != getattr(consideration, attribute) or not getattr(
                    consideration, attribute
                ):
                    from_value = getattr(consideration, attribute)
                    setattr(consideration, attribute, data)
                    to_value = data

            case "stage":
                data = Stage(form.data.get(attribute))
                if data != consideration.stage:
                    from_value = consideration.stage
                    setattr(consideration, attribute, data)
                consideration.stage = Stage(form.stage.data)
                to_value = data

            case _:
                data = None

        # TODO: using attribute for field name, is actually name on the model class
        # which is a little unclear for users, create a map of field names to something
        # more user friendly
        if from_value or to_value:
            if from_value is not None and isinstance(from_value, Enum):
                from_value = from_value.value
            if to_value is not None and isinstance(to_value, Enum):
                to_value = to_value.value
            user = session.get("user", "unknown user")

            change_log = ChangeLog(
                field=attribute,
                change={"from": from_value, "to": to_value},
                user=user,
                reason=form.reason.data if attribute == "stage" else None,
            )

            if consideration.change_log is None:
                consideration.changes = []

            consideration.change_log.append(change_log)

        if is_new:
            consideration.set_slug()

    return consideration


def _extract_changes_of_type(consideration, attr_name):
    if consideration.change_log is None:
        return None
    return [change for change in consideration.change_log if attr_name == change.field]


@planning_consideration.route("/")
def considerations():

    public_only = False if session.get("user") else True
    if public_only:
        query = Consideration.query.filter(Consideration.public == public_only)
    else:
        query = Consideration.query

    stage_param = []
    if "stage" in request.args:
        stage_selections = set([])
        for selection in request.args.getlist("stage"):
            try:
                stage = Stage(selection)
                stage_selections.add(stage)
            except ValueError:
                continue
            stage_selections.add(stage)
        stage_param = stage_selections
        filter_condition = Consideration.stage.in_(stage_selections)
        query = query.filter(filter_condition)

    # Keep include archived to keep bookmarked URLs working, but don't show it in the UI
    archived_param = request.args.get("include_archived")
    if not archived_param and Stage.ARCHIVED not in stage_param:
        query = query.filter(Consideration.stage != Stage("Archived"))

    legislation_param = request.args.get("legislation")
    if legislation_param:
        if legislation_param == "recorded":
            query = query.filter(Consideration.legislation.isnot(None))
        else:
            query = query.filter(Consideration.legislation.is_(None))

    tags_param = request.args.getlist("tag")
    if tags_param:
        query = query.filter(Consideration.tags.any(Tag.name.in_(tags_param)))

    blocked_param = request.args.get("show_only_blocked")
    if blocked_param:
        query = query.filter(
            and_(
                Consideration.blocked_reason.isnot(None),
                Consideration.blocked_reason != "",
            )
        )

    publishing_orgs_param = request.args.getlist("publishing-organisations")
    if publishing_orgs_param:
        query = query.filter(
            Consideration.answers.any(
                and_(
                    Answer.question_slug == "publishing-organisations",
                    or_(
                        *[
                            Answer.answer["choice"].astext.ilike(f"%{org}%")
                            for org in publishing_orgs_param
                        ]
                    ),
                )
            )
        )

    considerations = (
        query.filter(Consideration.deleted_date.is_(None))
        .order_by(Consideration.name.asc())
        .all()
    )

    # Calculate latest change for each consideration
    for consideration in considerations:
        if consideration.change_log is not None and len(consideration.change_log) > 0:
            change_dates = [change.created for change in consideration.change_log]
            consideration.latest_change = max(change_dates)
        else:
            consideration.latest_change = None

    tags = Tag.query.order_by(Tag.name).all()

    return render_template(
        "considerations.html",
        considerations=considerations,
        stages=Stage,
        stage_filter=[slugify(stage.name) for stage in stage_param],
        legislation_filter=legislation_param,
        show_only_blocked=blocked_param,
        publishing_organisations=publishing_organisations,
        publishing_orgs_filter=publishing_orgs_param,
        tags=tags,
        tags_filter=tags_param,
    )


@planning_consideration.route("/planning-considerations.csv")
def considerations_csv():

    data = []
    considerations = Consideration.query.filter(Consideration.public.is_(True)).all()
    for consideration in considerations:
        try:
            model = ConsiderationModel.model_validate(consideration)
            data.append(model.model_dump(by_alias=True))
        except Exception as e:
            print(f"Error: {e}")

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=data[0].keys())
    writer.writeheader()
    for row in data:
        writer.writerow(row)

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment;filename=planning-considerations.csv"
        },
    )


@planning_consideration.route("/<slug>")
def consideration(slug):
    consideration = Consideration.query.filter(Consideration.slug == slug).first()

    # handle incorrect consideration slugs
    if consideration is None:
        message = Markup(
            (
                "<p>We don't recognise <span class='govuk-!-font-weight-bold'>"
                f"{slug}</span>, maybe the spelling is different.</p><p>Use our "
                "<a class='govuk-list' href='#filter-considerations-list'>search</a>"
                " to see if the planning consideration exists.</p>"
            )
        )
        flash(message)
        return redirect(url_for("planning_consideration.considerations"))

    latest_change = None
    if consideration.change_log is not None and len(consideration.change_log) > 0:
        change_dates = [change.created for change in consideration.change_log]
        latest_change = max(change_dates)

    notes = [note for note in consideration.notes if note.deleted_date is None]
    notes.sort(key=lambda note: (note.created), reverse=True)

    return render_template(
        "consideration.html",
        consideration=consideration,
        latest_change=latest_change,
        stages=Stage,
        notes=notes,
    )


@planning_consideration.route("/add", methods=["GET", "POST"])
@login_required
def new():
    form = ConsiderationForm()

    # Set up tag choices
    form.tags.choices = [
        (str(tag.id), tag.name) for tag in Tag.query.order_by(Tag.name).all()
    ]

    if form.validate_on_submit():
        attributes = ["name", "github_discussion_number", "description", "public"]
        consideration = _create_or_update_consideration(form, attributes, is_new=True)
        tag_id = form.tags.data
        if tag_id:
            tag = Tag.query.get(tag_id)
            if tag is not None:
                consideration.tags.append(tag)
        db.session.add(consideration)
        db.session.commit()
        return redirect(
            url_for("planning_consideration.consideration", slug=consideration.slug)
        )

    return render_template("consideration-form.html", form=form)


@planning_consideration.route("/<slug>/edit", methods=["GET", "POST"])
@login_required
def edit(slug):
    consideration = Consideration.query.filter(Consideration.slug == slug).one_or_404()
    form = ConsiderationForm(obj=consideration)

    # Set up tag choices
    form.tags.choices = [
        (str(tag.id), tag.name) for tag in Tag.query.order_by(Tag.name).all()
    ]

    # Set initial tag selection
    if not form.is_submitted():
        if consideration.tags:
            form.tags.data = str(consideration.tags[0].id)

    if form.validate_on_submit():
        attributes = ["name", "github_discussion_number", "description", "public"]
        consideration = _create_or_update_consideration(
            form, attributes, consideration=consideration
        )

        # Update tags
        consideration.tags = []
        selected_tags = request.form.getlist("selected-tags")
        if selected_tags:
            for tag_id in selected_tags[0].split(","):
                if tag_id:
                    tag = Tag.query.get(tag_id)
                    if tag is not None:
                        consideration.tags.append(tag)

        db.session.add(consideration)
        db.session.commit()
        return redirect(url_for("planning_consideration.consideration", slug=slug))

    return render_template(
        "consideration-form.html", consideration=consideration, form=form, mode="edit"
    )


@planning_consideration.route("/<slug>/delete", methods=["GET", "POST"])
@login_required
def delete(slug):
    consideration = Consideration.query.filter(Consideration.slug == slug).one_or_404()
    form = DeleteForm()

    if form.validate_on_submit():
        if true_false_to_bool(form.confirm.data):
            consideration.delete()
            return redirect(url_for("planning_consideration.considerations"))
        return redirect(url_for("planning_consideration.consideration", slug=slug))

    return render_template(
        "delete.html",
        caption="Planning consideration",
        consideration=consideration,
        to_delete=consideration.name,
        form=form,
        cancel_link=url_for("planning_consideration.consideration", slug=slug),
    )


@planning_consideration.route("/<slug>/edit-specification", methods=["GET", "POST"])
@login_required
def edit_specification(slug):
    consideration = Consideration.query.filter(Consideration.slug == slug).one_or_404()
    form = LinkForm()

    if form.validate_on_submit():
        consideration = _create_or_update_consideration(
            form, ["specification"], consideration=consideration
        )
        db.session.add(consideration)
        db.session.commit()
        return redirect(url_for("planning_consideration.consideration", slug=slug))

    if consideration.specification is not None:
        form.link_text.data = consideration.specification["link_text"]
        form.link_url.data = consideration.specification["link_url"]

    page = {"title": "Specification URL"}

    return render_template(
        "questiontypes/input.html",
        consideration=consideration,
        form=form,
        mode="edit",
        page=page,
    )


@planning_consideration.route("/<slug>/add-schema", methods=["GET", "POST"])
@login_required
def add_schema(slug):
    consideration = Consideration.query.filter(Consideration.slug == slug).one_or_404()
    form = DatasetForm()

    if form.validate_on_submit():
        consideration = _create_or_update_consideration(
            form, ["dataset"], consideration=consideration
        )
        db.session.add(consideration)
        db.session.commit()
        return redirect(url_for("planning_consideration.consideration", slug=slug))

    page = {"title": "Add dataset schema url", "submit_text": "Save"}

    return render_template(
        "questiontypes/input.html", consideration=consideration, form=form, page=page
    )


@planning_consideration.get("/<slug>/remove-schema/<dataset_name>")
@login_required
def remove_schema(slug, dataset_name):
    consideration = Consideration.query.filter(Consideration.slug == slug).one_or_404()
    for dataset in consideration.datasets:
        if dataset["name"] == dataset_name:
            consideration.datasets.remove(dataset)
            db.session.add(consideration)
            db.session.commit()
            break
    return redirect(url_for("planning_consideration.consideration", slug=slug))


@planning_consideration.route(
    "/<slug>/<attr_name>/<link_text>/delete",
    methods=["GET", "POST"],
)
@login_required
def delete_attr_link(slug, attr_name, link_text):
    consideration = Consideration.query.filter(Consideration.slug == slug).one_or_404()

    # find matches
    has_changed = False
    links = getattr(consideration, attr_name)
    for link in links:
        if link["link_text"] == link_text:
            links.remove(link)
            has_changed = True

    if has_changed:
        from_value = getattr(consideration, attr_name)
        setattr(consideration, attr_name, links)
        to_value = getattr(consideration, attr_name)
        user = session.get("user", "unknown user")

        change_log = ChangeLog(
            field=attr_name, change={"from": from_value, "to": to_value}, user=user
        )
        if consideration.change_log is None:
            consideration.changes = []
        consideration.change_log.append(change_log)
        db.session.add(consideration)
        db.session.commit()

    return redirect(url_for("planning_consideration.consideration", slug=slug))


@planning_consideration.route("/<slug>/edit-estimated-size", methods=["GET", "POST"])
@login_required
def edit_estimated_size(slug):
    consideration = Consideration.query.filter(Consideration.slug == slug).one_or_404()
    form = ExpectedSizeForm(obj=consideration)

    if form.validate_on_submit():
        consideration = _create_or_update_consideration(
            form, ["expected_number_of_records"], consideration=consideration
        )
        db.session.add(consideration)
        db.session.commit()
        return redirect(url_for("planning_consideration.consideration", slug=slug))

    page = {"title": "Expected number of records"}

    return render_template(
        "questiontypes/input.html",
        consideration=consideration,
        form=form,
        mode="edit",
        page=page,
    )


@planning_consideration.route("/<slug>/add-synonym", methods=["GET", "POST"])
@login_required
def add_synonym(slug):
    consideration = Consideration.query.filter(Consideration.slug == slug).one_or_404()
    form = SynonymForm(obj=consideration)

    if form.validate_on_submit():
        consideration = _create_or_update_consideration(
            form, ["synonym"], consideration=consideration
        )
        db.session.add(consideration)
        db.session.commit()
        return redirect(url_for("planning_consideration.consideration", slug=slug))

    page = {"title": "Add synonym", "submit_text": "Save synonym"}

    return render_template(
        "questiontypes/input.html",
        consideration=consideration,
        form=form,
        mode="edit",
        page=page,
    )


@planning_consideration.route(
    "/<slug>/synonym/<synonym>/delete", methods=["GET", "POST"]
)
@login_required
def delete_synonym(slug, synonym):
    consideration = Consideration.query.filter(Consideration.slug == slug).one_or_404()
    from_value = consideration.synonyms
    consideration.synonyms.remove(synonym)
    to_value = consideration.synonyms
    user = session.get("user", "unknown user")

    change_log = ChangeLog(
        field="synonym", change={"from": from_value, "to": to_value}, user=user
    )
    if consideration.change_log is None:
        consideration.changes = []

    consideration.change_log.append(change_log)

    db.session.add(consideration)
    db.session.commit()
    return redirect(url_for("planning_consideration.consideration", slug=slug))


@planning_consideration.route("/<slug>/prioritised", methods=["GET", "POST"])
@login_required
def prioritised(slug):
    consideration = Consideration.query.filter(Consideration.slug == slug).one_or_404()
    form = PriorityForm(obj=consideration)

    if form.validate_on_submit():
        consideration = _create_or_update_consideration(
            form, ["prioritised"], consideration=consideration
        )
        db.session.add(consideration)
        db.session.commit()
        return redirect(url_for("planning_consideration.consideration", slug=slug))

    page = {"title": "Set prioritisation", "submit_text": "Set prioritisation"}

    return render_template(
        "questiontypes/input.html", consideration=consideration, form=form, page=page
    )


@planning_consideration.route("/<slug>/public", methods=["GET", "POST"])
@login_required
def public(slug):
    consideration = Consideration.query.filter(Consideration.slug == slug).one_or_404()
    form = PublicForm(obj=consideration)

    if form.validate_on_submit():
        consideration = _create_or_update_consideration(
            form, ["public"], consideration=consideration
        )
        db.session.add(consideration)
        db.session.commit()
        return redirect(url_for("planning_consideration.consideration", slug=slug))

    page = {"title": "Set public or private", "submit_text": "Set"}

    return render_template(
        "questiontypes/input.html", consideration=consideration, form=form, page=page
    )


@planning_consideration.route("/<slug>/stage")
def stage(slug):
    consideration = Consideration.query.filter(Consideration.slug == slug).one_or_404()

    stage_changes = _extract_changes_of_type(consideration, "stage")
    return render_template(
        "stage.html", consideration=consideration, stage_changes=stage_changes
    )


@planning_consideration.route("/<slug>/stage/change", methods=["GET", "POST"])
@login_required
def change_stage(slug):
    consideration = Consideration.query.filter(Consideration.slug == slug).one_or_404()
    form = StageForm()

    if form.validate_on_submit():
        consideration = _create_or_update_consideration(
            form, ["stage"], consideration=consideration
        )
        db.session.add(consideration)
        db.session.commit()
        return redirect(url_for("planning_consideration.consideration", slug=slug))

    form.stage.data = consideration.stage.value

    page = {"title": "Update stage", "submit_text": "Update"}

    return render_template(
        "questiontypes/input.html", consideration=consideration, form=form, page=page
    )


@planning_consideration.route("/<slug>/os-declaration", methods=["GET", "POST"])
@login_required
def change_os_declaration(slug):
    consideration = Consideration.query.filter(Consideration.slug == slug).one_or_404()
    form = OSDeclarationForm()

    if form.validate_on_submit():
        print(OSDeclarationStatus(form.status.data))
        consideration = _create_or_update_consideration(
            form, ["os_declaration"], consideration=consideration
        )
        db.session.add(consideration)
        db.session.commit()
        return redirect(url_for("planning_consideration.consideration", slug=slug))

    # populate form with existing values
    form.status.data = (
        consideration.os_declaration["status"]
        if consideration.os_declaration
        else OSDeclarationStatus.UNKNOWN.value
    )
    form.further_information_url.data = (
        consideration.os_declaration["further_information_url"]
        if consideration.os_declaration
        else None
    )

    page = {"title": "Update OS declaration", "submit_text": "Update"}

    return render_template(
        "questiontypes/input.html", consideration=consideration, form=form, page=page
    )


@planning_consideration.route("/<slug>/edit-frequency", methods=["GET", "POST"])
@login_required
def frequency(slug):
    consideration = Consideration.query.filter(Consideration.slug == slug).one_or_404()
    form = FrequencyForm()

    if form.validate_on_submit():
        consideration = _create_or_update_consideration(
            form, ["frequency_of_updates"], consideration=consideration
        )
        db.session.add(consideration)
        db.session.commit()
        return redirect(url_for("planning_consideration.consideration", slug=slug))

    form.frequency_of_updates.data = (
        consideration.frequency_of_updates.value
        if consideration.frequency_of_updates
        else ""
    )

    page = {"title": "Edit expected frequency of updates", "submit_text": "Save"}

    return render_template(
        "questiontypes/input.html", consideration=consideration, form=form, page=page
    )


@planning_consideration.route("/<slug>/add-useful-link", methods=["GET", "POST"])
@login_required
def add_useful_link(slug):
    consideration = Consideration.query.filter(Consideration.slug == slug).one_or_404()
    form = LinkForm()

    if form.validate_on_submit():
        consideration = _create_or_update_consideration(
            form, ["useful_links"], consideration=consideration
        )
        db.session.add(consideration)
        db.session.commit()
        return redirect(url_for("planning_consideration.consideration", slug=slug))

    page = {"title": "Add useful link", "submit_text": "Save link"}

    return render_template(
        "questiontypes/input.html", consideration=consideration, form=form, page=page
    )


@planning_consideration.route("/<slug>/edit-legislation", methods=["GET", "POST"])
@login_required
def edit_legislation(slug):
    consideration = Consideration.query.filter(Consideration.slug == slug).one_or_404()
    form = LinkForm(url_required=False)

    if form.validate_on_submit():
        consideration = _create_or_update_consideration(
            form, ["legislation"], consideration=consideration
        )
        db.session.add(consideration)
        db.session.commit()
        return redirect(url_for("planning_consideration.consideration", slug=slug))

    if consideration.legislation is not None:
        form.link_text.data = consideration.legislation["link_text"]
        form.link_url.data = consideration.legislation["link_url"]

    page = {"title": "Edit legislation", "submit_text": "Save"}

    return render_template(
        "questiontypes/input.html", consideration=consideration, form=form, page=page
    )


@planning_consideration.route("/<slug>/note", methods=["GET", "POST"])
@login_required
def add_note(slug):
    consideration = Consideration.query.filter(Consideration.slug == slug).one_or_404()
    form = NoteForm()
    if form.validate_on_submit():
        note = Note(
            text=form.text.data,
            author=session.get("user", "unknown"),
        )
        if consideration.notes is None:
            consideration.notes = []
        consideration.notes.append(note)

        db.session.add(consideration)
        db.session.commit()
        return redirect(url_for("planning_consideration.consideration", slug=slug))

    page = {"title": "Add note", "submit_text": "Save note"}

    return render_template(
        "note-form.html", consideration=consideration, form=form, page=page
    )


@planning_consideration.route("/<slug>/note/<note_id>", methods=["GET", "POST"])
@login_required
def edit_note(slug, note_id):
    consideration = Consideration.query.filter(Consideration.slug == slug).one_or_404()
    note = Note.query.get(note_id)
    if note is None or note.deleted_date is not None:
        abort(404)

    form = NoteForm(obj=note)

    if form.validate_on_submit():
        note.text = form.text.data
        note.author = session.get("user", "unknown")

        db.session.add(note)
        db.session.commit()
        return redirect(url_for("planning_consideration.consideration", slug=slug))

    page = {"title": "Edit note", "submit_text": "Update note"}

    return render_template(
        "note-form.html", consideration=consideration, form=form, page=page, note=note
    )


@planning_consideration.get("/<slug>/note/<note_id>/delete")
@login_required
def delete_note(slug, note_id):
    note = Note.query.get(note_id)
    note.deleted_date = datetime.date.today()
    db.session.add(note)
    db.session.commit()
    return redirect(url_for("planning_consideration.consideration", slug=slug))


@planning_consideration.route("/<slug>/block", methods=["GET", "POST"])
@login_required
def block(slug):
    consideration = Consideration.query.filter(Consideration.slug == slug).one_or_404()
    form = BlockedForm()

    if form.validate_on_submit():

        if consideration.blocked_reason is None:
            consideration.blocked_reason = form.reason.data
        # To do: handle if reason is already captured

        db.session.add(consideration)
        db.session.commit()
        return redirect(url_for("planning_consideration.consideration", slug=slug))

    page = {"title": "Mark as blocked", "submit_text": "Block"}

    return render_template(
        "block-form.html", consideration=consideration, form=form, page=page
    )


@planning_consideration.get("/<slug>/unblock")
@login_required
def unblock(slug):
    consideration = Consideration.query.filter(Consideration.slug == slug).one_or_404()
    consideration.blocked_reason = None
    db.session.add(consideration)
    db.session.commit()
    return redirect(url_for("planning_consideration.consideration", slug=slug))


@planning_consideration.route("/<slug>/change-log")
@login_required
def change_log(slug):
    consideration = Consideration.query.filter(Consideration.slug == slug).one_or_404()
    if consideration.change_log is None:
        return abort(404)
    return render_template(
        "change-log.html", consideration=consideration, content_primary_width="full"
    )
