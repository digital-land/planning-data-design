from flask import Blueprint, render_template

help = Blueprint(
    "help",
    __name__,
    url_prefix="/help",
)


@help.route("/os-declaration-options")
def os_declaration_options():
    return render_template("help/os-declaration-options.html")
