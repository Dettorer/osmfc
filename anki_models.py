import genanki  # type: ignore


SCRIPT = """
<script>
    var feature_shape = document.getElementById("{{OSMID}}");
    feature_shape.style.setProperty("opacity", "1");
</script>
"""


def make_anki_model(deck_id: int, map_image: str) -> genanki.Model:
    """Build an anki model with the given map embedded"""

    return genanki.Model(
        deck_id + 1,  # Model ID
        f"OpenStreetMap features for deck {deck_id}",
        fields=[
            {"name": "FeatureName"},  # The name of the OSM feature
            {"name": "OSMID"},  # The ID used to identify the feature's in the SVG map
            {"name": "URL"},  # The feature's URL on openstreetmap.org
        ],
        templates=[
            # TODO: the SVG is embedded four times, wasting a lot of space, we should
            # save it to a file instead. But be careful not to use a field to store the
            # file name, as anki does not support constructions like
            #     <img src="{{FileName}}">
            # in templates.
            {
                "name": "Card 1",
                "qfmt": ("Where is {{FeatureName}}?<br>\n" + map_image),
                "afmt": (
                    "<hr id=answer>\n" + map_image + "<br>\n"
                    "{{FeatureName}}<br>\n"
                    '(OSM url: <a href="{{URL}}">{{URL}}</a>)\n' + SCRIPT
                ),
            },
            {
                "name": "Card 2",
                "qfmt": ("What is this?<br>\n" + map_image + SCRIPT),
                "afmt": (
                    "<hr id=answer>\n" + map_image + "<br>"
                    "{{FeatureName}}<br>\n"
                    '(OSM url: <a href="{{URL}}">{{URL}}</a>)\n' + SCRIPT
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
