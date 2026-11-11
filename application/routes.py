import csv
import io

from flask import Response, abort, redirect, render_template, request

from application.content import breadcrumbs

ERRORS = {
    404: "Page not found",
    405: "Method not allowed",
    410: "Page removed",
}
CSV_PATH = "/consideration/planning-considerations.csv"
GENERATED_PATHS = (CSV_PATH,)
CSV_FIELDS = [
    "name",
    "slug",
    "description",
    "stage",
    "tags",
    "datasets",
    "frequency_of_updates",
    "github_discussion_number",
    "updated",
]


def considerations_csv(considerations):
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(CSV_FIELDS)
    for page in considerations:
        meta = page.meta
        writer.writerow(
            [
                page.title,
                page.slug,
                page.description,
                meta.get("stage", ""),
                ";".join(meta.get("tags", [])),
                ";".join(meta.get("datasets", [])),
                meta.get("frequency_of_updates", ""),
                meta.get("github_discussion_number", ""),
                meta.get("updated", ""),
            ]
        )
    return out.getvalue()


def register_routes(app, pages, redirects):
    considerations = sorted(
        (p for p in pages.values() if p.template == "consideration"),
        key=lambda p: p.title.lower(),
    )
    csv_text = considerations_csv(considerations)

    @app.get(CSV_PATH)
    def csv_export():
        return Response(csv_text, mimetype="text/csv")

    @app.get("/", defaults={"path": ""})
    @app.get("/<path:path>")
    def serve(path):
        url = "/" + path
        page = pages.get(url.rstrip("/") or "/")
        if page:
            return render_template(
                f"{page.template}.html",
                page=page,
                breadcrumbs=breadcrumbs(pages, page.path),
                considerations=considerations,
            )
        hit = redirects.resolve(
            url, request.query_string.decode("utf-8", "replace"), pages
        )
        if hit is None:
            abort(404)
        location, status = hit
        if status == 410:
            abort(410)
        return redirect(location, code=status)

    def error(e):
        return (
            render_template("error.html", code=e.code, heading=ERRORS[e.code]),
            e.code,
        )

    for code in ERRORS:
        app.register_error_handler(code, error)
