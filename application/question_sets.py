from application.models import Stage

questions = {
    Stage.BACKLOG: {
        "who-asked-for-it": {
            "question": "Who asked for '{name}' data?",
            "type": "input",
            "next": "what-is-the-driver",
        },
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
            "next": "which-focus-area-does-it-support",
            "prev": "who-asked-for-it",
        },
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
        },
    },
    Stage.SCREEN: {
        "what-is-the-planning-consideration": {
            "question": "What is the '{name}' consideration?",
            "type": "textarea",
            "hint": """Provide a description of this planning consideration.
            The common name for the planning consideration should be used here""",
            "next": "is-there-legislation",
        },
        "is-there-legislation": {
            "question": "Is there legislation that defines '{name}'?",
            "type": "choose-one-from-list",
            "choices": ["Yes", "No"],
            "hint": """Tell us where it is""",
            "prev": "what-is-the-planning-consideration",
            "next": "what-is-the-legislation-that-defines",
        },
        "what-is-the-legislation-that-defines": {
            "question": "What is the legislation that defines how a '{name}' gets designated?",
            "type": "textarea",
            "hint": """We are looking for the legislation that specifically sets out who,
            where applicable, are the parties who are able to designate the planning consideration""",
            "prev": "is-there-legislation",
            "next": "which-focus-area-does-it-support",
        },
        "what-is-the-legislation-for-publication": {
            "question": "What is the legislation that requires the publication of '{name}'?",
            "type": "textarea",
            "hint": """We are looking for the legislation that specifically
            mentions data/registers or other""",
            "prev": "what-is-the-legislation-that-defines",
            "next": "who-in-law-is-responsible-for-it",
        },
        "who-in-law-is-responsible-for-it": {
            "question": "Who, in law, is responsible for the planning consideration or makes decisions about '{name}'?",
            "type": "textarea",
            "hint": """We are looking for the legislation that imposes this accountability on an organisation""",
            "prev": "what-is-the-legislation-for-publication",
            "next": "which-organisations-should-publish-it",
        },
    },
}
