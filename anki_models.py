import genanki

# Anki needs unique Model ID, this one was generated randomly with
# random.randrange(1 << 30, 1 << 31)
OSM_FEATURE_MODEL_ID = 1275901851
# an Anki note model based on genanki.BASIC_AND_REVERSED_CARD_MODEL
OSM_FEATURE_MODEL = genanki.Model(
    OSM_FEATURE_MODEL_ID,
    "OpenStreetMap features",
    fields=[
        {"name": "Front", "font": "Arial"},
        {"name": "Back", "font": "Arial"},
        {"name": "URL", "font": "Arial"},  # The feature's URL on openstreetmap.org
    ],
    templates=[
        {
            "name": "Card 1",
            "qfmt": "{{Front}}",
            "afmt": (
                "{{FrontSide}}\n\n"
                "<hr id=answer>\n\n"
                "{{Back}}<br>\n\n"
                '(OSM url: <a href="{{URL}}">{{URL}}</a>)'
            ),
        },
        {
            "name": "Card 2",
            "qfmt": "{{Back}}",
            "afmt": (
                "{{FrontSide}}\n\n"
                "<hr id=answer>\n\n"
                "{{Front}}<br>\n\n"
                '(OSM url: <a href="{{URL}}">{{URL}}</a>)'
            ),
        },
    ],
    css=(
        ".card {\n"
        "font-family: arial;\n"
        "font-size: 20px;\n"
        "text-align: center;\n"
        "color: black;\n"
        "background-color: white;\n"
        "}\n"
    ),
)
