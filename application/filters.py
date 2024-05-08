def slugify_filter(s):
    return s.lower().replace(" ", "-").replace(",", "")


def map_to_tag_class_filter(s):
    stage_to_class = {
        "Backlog": "govuk-tag--grey",
        "On the platform": "govuk-tag--green",
        "Archived": "govuk-tag--orange",
    }
    if s in stage_to_class.keys():
        return stage_to_class[s]
    return "govuk-tag--blue"


def choice_to_list_filter(s):
    return s.split(";")
