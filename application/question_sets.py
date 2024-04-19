from application.models import Stage

questions = {
    Stage.BACKLOG: [
        {
            "who-asked-for-it": {
                "question": "Who asked for '{name}' data?",
                "type": "input",
                "next": {
                    "type": "url",
                    "url": "what-is-the-driver",
                },
            }
        },
        {
            "what-is-the-driver": {
                "question": "What is the driver for the request?",
                "type": "choose-one-from-list",
                "choices": [
                    "National policy change",
                    "Ministerial priority",
                    "Specific user requirement",
                    "LPA requirement",
                    "Existing planning requirement",
                ],
                "next": {
                    "type": "url",
                    "url": "which-focus-area-does-it-support",
                },
                "prev": "who-asked-for-it",
            }
        },
        {
            "which-focus-area-does-it-support": {
                "question": "Which 2024 focus area does the request support?",
                "type": "choose-one-from-list-other",
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
    Stage.RESEARCH: [
        {
            "lifecycle": {
                "question": "What is the (high-level) lifecycle of a {name}?",
                "type": "textarea",
                "hint": """Provide details on designation and de-designation.""",
                "next": {
                    "type": "url",
                    "url": "is-a-data-standard-required",
                },
            }
        },
        {
            "how-is-data-created": {
                "question": "Do we understand how the data is created/produced?",
                "type": "textarea",
                "hint": """What is the recipe? How do we think the publisher does this?""",
                "prev": "lifecycle",
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
                    "type": "url",
                    "url": "is-there-legislation",
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
                        {"url": "what-is-the-legislation-that-defines", "value": "Yes"}
                    ],
                    "default_url": "who-in-law-is-responsible-for-it",
                },
            }
        },
        {
            "what-is-the-legislation-that-defines": {
                "question": "What is the legislation that defines how a '{name}' gets designated?",
                "type": "textarea",
                "hint": """We are looking for the legislation that specifically sets out who,
            where applicable, are the parties who are able to designate the planning consideration""",
                "prev": "is-there-legislation",
                "next": {
                    "type": "url",
                    "url": "what-is-the-legislation-for-publication",
                },
            }
        },
        {
            "what-is-the-legislation-for-publication": {
                "question": "What is the legislation that requires the publication of '{name}'?",
                "type": "textarea",
                "hint": """We are looking for the legislation that specifically
            mentions data/registers or other""",
                "prev": "what-is-the-legislation-that-defines",
                "next": {
                    "type": "url",
                    "url": "who-in-law-is-responsible-for-it",
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
                    "type": "url",
                    "url": "publishing-organisations",
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
                    "type": "url",
                    "url": "is-it-a-trigger",
                },
            }
        },
        {
            "is-it-a-trigger": {
                "question": "Is the {name} a trigger?",
                "type": "choose-one-from-list",
                "choices": ["Yes", "No"],
                "hint": """Considerations can trigger a need to do something or a series of things.""",
                "prev": "publishing-organisations",
                # this needs a logic gate here
                "next": {
                    "type": "url",
                    "url": "what-is-triggered",
                },
            }
        },
        {
            "what-is-triggered": {
                "question": "What is triggered by {name}?",
                "type": "textarea",
                "prev": "publishing-organisations",
                "next": {
                    "type": "url",
                    "url": "is-it-consulted",
                },
            }
        },
        {
            "is-it-consulted": {
                "question": "Is the {name} something to consult?",
                "type": "choose-one-from-list",
                "choices": ["Yes", "No"],
                "hint": """Some considerations are consulted when performing tasks within the planning system.""",
                "prev": "is-it-a-trigger",
                "next": {
                    "type": "url",
                    "url": "is-consulted",
                },
            }
        },
        {
            "is-consulted": {
                "question": "Provide information about when {name} is consulted",
                "type": "textarea",
                "hint": """Some considerations are consulted when performing tasks within the planning system.""",
                "prev": "is-it-consulted",
                "next": {
                    "type": "url",
                    "url": "existing-data",
                },
            }
        },
        {
            "existing-data": {
                "question": "Is there any {name} data already available?",
                "type": "choose-one-from-list",
                "choices": ["Yes", "No"],
                "prev": "is-it-consulted",
                # needs logic gate
                "next": {
                    "type": "url",
                    "url": "existing-data-examples",
                },
            }
        },
        {
            "existing-data-examples": {
                "question": "What {name} data is currently available?",
                "type": "textarea",
                "hint": """Capture examples of any data currently available.""",
                "prev": "is-it-consulted",
                "next": {
                    "type": "url",
                    "url": "single-source",
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
                    "type": "url",
                    "url": "is-a-data-standard-required",
                },
            }
        },
        {
            "is-a-data-standard-required": {
                "question": "Will a data standard be required?",
                "type": "choose-one-from-list",
                "choices": ["Yes", "No"],
                "prev": "single-source",
            }
        },
    ],
}
