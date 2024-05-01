from application.models import Stage

questions = {
    Stage.BACKLOG: [
        {
            "who-asked-for-it": {
                "question": "Who asked for '{name}' data?",
                "type": "input",
                "hint": """Give a specific name and role. E.g. Eloise, policy.""",
                "next": {
                    "type": "slug",
                    "slug": "what-is-the-driver",
                },
            }
        },
        {
            "what-is-the-driver": {
                "question": "What is the driver for the request?",
                "type": "choose-one-from-list",  # should it accept multiple?
                "choices": [
                    "National policy change",
                    "Ministerial priority",
                    "Specific user requirement",
                    "LPA requirement",
                    "Existing planning requirement",
                    "Other",
                ],
                "next": {
                    "type": "slug",
                    "slug": "which-focus-area-does-it-support",
                },
                "prev": "who-asked-for-it",
            }
        },
        {
            "which-focus-area-does-it-support": {
                "question": "Which 2024 focus area does the request support?",
                "type": "choose-one-or-more",
                "choices": [
                    "Modern planning software",
                    "Faster local plans",
                    "Included in LURA",
                    "Other",
                ],
                "prev": "what-is-the-driver",
            }
        },
    ],
    Stage.SCREEN: [
        {
            "what-is-the-planning-consideration": {
                "question": "What is the '{name}' consideration?",
                "type": "textarea",
                "hint": """Provide a description of this planning consideration.
            The common name for the planning consideration should be used here""",
                "next": {
                    "type": "slug",
                    "slug": "is-there-legislation",
                },
            }
        },
        {
            "is-there-legislation": {
                "question": "Is there legislation that defines '{name}'?",
                "type": "choose-one-from-list",
                "choices": ["Yes", "No"],
                "hint": """Tell us where it is""",
                "prev": "what-is-the-planning-consideration",
                "next": {
                    "type": "condition",
                    "conditions": [
                        {"slug": "what-is-the-legislation-that-defines", "value": "Yes"}
                    ],
                    "default_slug": "who-in-law-is-responsible-for-it",
                },
            }
        },
        {
            "what-is-the-legislation-that-defines": {
                "question": "What is the legislation that defines '{name}'?",
                "type": "textarea",
                "hint": """We are looking for the legislation that specifically sets what the consideration is and why it matters in planning.""",
                "prev": "is-there-legislation",
                "next": {
                    "type": "slug",
                    "slug": "what-is-the-legislation-that-defines-designation",
                },
            }
        },
        {
            "what-is-the-legislation-that-defines-designation": {
                "question": "What is the specific part of the legislation that describes how a '{name}' gets designated?",
                "type": "textarea",
                "hint": """We are looking for the legislation that specifically sets out who,
            where applicable, are the parties who are able to designate the planning consideration""",
                "prev": "what-is-the-legislation-that-defines",
                "next": {
                    "type": "slug",
                    "slug": "what-is-the-legislation-for-publication",
                },
            }
        },
        {
            "what-is-the-legislation-for-publication": {
                "question": "What is the specific part of the legislation that requires the publication of '{name}'?",
                "type": "textarea",
                "hint": """We are looking for the legislation that specifically
            mentions data/registers or other""",
                "prev": "what-is-the-legislation-that-defines-designation",
                "next": {
                    "type": "slug",
                    "slug": "who-in-law-is-responsible-for-it",
                },
            }
        },
        {
            "who-in-law-is-responsible-for-it": {
                "question": "Who, in law, is responsible for the planning consideration or makes decisions about '{name}'?",
                "type": "textarea",
                "hint": """We are looking for the legislation that imposes this accountability on an organisation""",
                "prev": "what-is-the-legislation-for-publication",
                "next": {
                    "type": "slug",
                    "slug": "publishing-organisations",
                },
            }
        },
        {
            "publishing-organisations": {
                "question": "Which organisations do we think should publish the data?",
                "type": "textarea",
                "hint": """""",
                "prev": "who-in-law-is-responsible-for-it",
                "next": {
                    "type": "slug",
                    "slug": "is-it-a-trigger",
                },
            }
        },
        {
            "is-it-a-trigger": {
                "question": "Is the {name} a trigger?",
                "type": "choose-one-from-list",
                "choices": ["Yes", "No"],
                "hint": """Considerations can trigger a need to do something or a series of things.""",  # it triggers a planning requirement
                "prev": "publishing-organisations",
                "next": {
                    "type": "condition",
                    "conditions": [
                        {"slug": "what-is-triggered", "value": "Yes"},
                        {"slug": "is-it-consulted", "value": "No"},
                    ],
                    "default_slug": "is-it-consulted",
                },
            }
        },
        {
            "what-is-triggered": {
                "question": "What needs to be done because {name} has acted as the trigger?",
                "type": "textarea",
                "prev": "is-it-a-trigger",
                "next": {
                    "type": "slug",
                    "slug": "is-it-consulted",
                },
            }
        },
        {
            "is-it-consulted": {
                "question": "Is the {name} something to consult during plan making?",
                "type": "choose-one-from-list",
                "choices": ["Yes", "No"],
                "hint": """Some considerations are consulted when performing tasks within the planning system.""",
                "prev": "is-it-a-trigger",
                "next": {
                    "type": "condition",
                    "conditions": [
                        {"slug": "is-consulted", "value": "Yes"},
                        {"slug": "existing-data", "value": "No"},
                    ],
                    "default_slug": "existing-data",
                },
            }
        },
        {
            "is-consulted": {
                "question": "Provide information about when {name} is used during plan making",
                "type": "textarea",
                "hint": """Some considerations are consulted when performing tasks within the planning system.""",
                "prev": "is-it-consulted",
                "next": {
                    "type": "slug",
                    "slug": "existing-data",
                },
            }
        },
        {
            "existing-data": {
                "question": "Is there any {name} data already available?",
                "type": "choose-one-from-list",
                "choices": ["Yes", "No"],
                "prev": "is-it-consulted",
                "next": {
                    "type": "condition",
                    "conditions": [
                        {"slug": "existing-data-examples", "value": "Yes"},
                        {"slug": "single-source", "value": "No"},
                    ],
                    "default_slug": "single-source",
                },
            }
        },
        {
            "existing-data-examples": {
                "question": "What {name} data is currently available?",
                "type": "add-to-a-list",
                "form": "ExistingDataForm",
                "hint": """Capture examples of any data currently available.""",
                "prev": "existing-data",
                "next": {
                    "type": "slug",
                    "slug": "single-source",
                },
            }
        },
        {
            "single-source": {
                "question": "Do we think the data should come from a single source?",
                "type": "textarea",
                "hint": """Some datasets should be published by a single organisation.""",
                "prev": "existing-data",
                "next": {
                    "type": "slug",
                    "slug": "is-a-data-standard-required",
                },
            }
        },
        {
            "is-a-data-standard-required": {
                "question": "Will a data standard be required?",
                "type": "choose-one-from-list",
                "hint": """We want to flag if we think we'll need to aggregate data from multiple providers.""",
                "choices": ["Yes", "No"],
                "prev": "single-source",
            }
        },
    ],
    Stage.RESEARCH: [
        {
            "lifecycle": {
                "question": "Do we understand the lifecycle of a {name}?",
                "type": "choose-one-from-list",
                "choices": ["Yes", "No"],
                "next": {
                    "type": "condition",
                    "conditions": [
                        {"slug": "lifecycle-stages", "value": "Yes"},
                        {"slug": "how-is-data-created", "value": "No"},
                    ],
                    "default_slug": "how-is-data-created",
                },
            }
        },
        {
            "lifecycle-stages": {
                "question": "Document a stage of the high-level lifecycle of a {name}",
                "type": "add-to-a-list",
                "form": "LifecycleStagesForm",
                "hint": """Provide details of the stage""",
                "prev": "lifecycle",
                "next": {
                    "type": "slug",
                    "slug": "how-is-data-created",
                },
            }
        },
        {
            "how-is-data-created": {
                "question": "Do we understand how the data is created/produced?",
                "type": "textarea",
                "hint": """What is the recipe? How do we think the publisher does this?""",
                "next": {
                    "type": "slug",
                    "slug": "where-is-data-used",
                },
                "prev": "lifecycle",
            }
        },
        {
            "where-is-data-used": {
                "question": "Where will or should the data be used?",
                "type": "textarea",
                "hint": "Where do we expect the data to be used and for what purpose.",
                "next": {
                    "type": "slug",
                    "slug": "related-planning-considerations",
                },
                "prev": "how-is-data-created",
            }
        },
        {
            "related-planning-considerations": {
                "question": "What other planning considerations does it interact with?",
                "type": "textarea",
                "hint": "List the planning considerations it interacts with. Try to explain how.",
                "next": {
                    "type": "slug",
                    "slug": "primary-users",
                },
                "prev": "where-is-data-used",
            }
        },
        {
            "primary-users": {
                "question": (
                    "Other than the statutory consultees who are the primary users of {name}? "
                    "How do we expect them to use {name}?"
                ),
                "type": "textarea",
                "hint": (
                    "List the actor or actors affected by the planning consideration, "
                    "include how we expect each actor to actually use the data, what will they do with it and why?"
                ),
                "next": {
                    "type": "slug",
                    "slug": "user-and-data-needs",
                },
                "prev": "related-planning-considerations",
            }
        },
        {
            "user-and-data-needs": {
                "question": "What are the (statutory) user/data needs?",
                "type": "textarea",
                "hint": "Either capture the needs here or link to where the needs have been recorded.",
                "next": {
                    "type": "slug",
                    "slug": "additional-users",
                },
                "prev": "primary-users",
            }
        },
        {
            "additional-users": {
                "question": "Who are the types of users who might benefit from having access to {name} data?",
                "type": "textarea",
                "hint": "These are actors who may find the data useful, but are not the statutory user.",
                "next": {
                    "type": "slug",
                    "slug": "use-cases",
                },
                "prev": "user-and-data-needs",
            }
        },
        {
            "use-cases": {
                "question": "What are some potential uses of {name} data?",
                "type": "textarea",
                "next": {
                    "type": "slug",
                    "slug": "value-to-platform",
                },
                "prev": "additional-users",
            }
        },
        {
            "value-to-platform": {
                "question": "What's the value of adding {name} data to the platform?",
                "type": "textarea",
                "hint": "Is there value in DLUHC investing time and effort in getting the data ready and re-publishing?",
                "next": {
                    "type": "slug",
                    "slug": "risks",
                },
                "prev": "use-cases",
            }
        },
        {
            "risks": {
                "question": "From what we have learnt so far are there any risks to making {name} data available?",
                "type": "textarea",
                "hint": (
                    "This could be things like, the multiple sources of data, unclear licensing, "
                    "lack of legislative driver, poor data quality, poorly defined requirements, "
                    "ongoing costs on LPA, DLUHC etc."
                ),
                "prev": "value-to-platform",
            }
        },
    ],
}
