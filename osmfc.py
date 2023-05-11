#!/usr/bin/env python3

import argparse
import functools
import genanki
import html
import osmium

from osmium.osm import types as otypes
from anki_models import OSM_FEATURE_MODEL


def _get_osm_url(o: otypes.OSMObject, object_type: str) -> str:
    return f"https://www.openstreetmap.org/{object_type}/{o.id}"


class MonumentHandler(osmium.SimpleHandler):
    """An osmium handler that creates flashcards about monument informations"""

    # Anki needs unique deck ID, this one was generated randomly with
    # random.randrange(1 << 30, 1 << 31)
    # TODO: this should be a combined hash of the OSM data and filtering information
    MONUMENTS_DECK_ID = 1725870212

    def __init__(self) -> None:
        super().__init__()
        self.flashcards = genanki.Deck(self.MONUMENTS_DECK_ID, "Monuments")

    def _handle_object(self, o: otypes.OSMObject, object_type: str) -> None:
        name = o.tags.get("name")
        if (
            o.tags.get("historic") == "monument" or o.tags.get("heritage") == "2"
        ) and name is not None:
            self.flashcards.add_note(
                genanki.Note(
                    model=OSM_FEATURE_MODEL,
                    fields=[name, str(o.id), html.escape(_get_osm_url(o, object_type))],
                )
            )

    node = functools.partialmethod(_handle_object, object_type="node")
    way = functools.partialmethod(_handle_object, object_type="way")
    relation = functools.partialmethod(_handle_object, object_type="relation")


if __name__ == "__main__":
    # Handle command line arguments
    parser = argparse.ArgumentParser(
        prog="osmfc", description="A flashcard generator based on OpenStreetMap data"
    )
    parser.add_argument(
        "osm_file",
        help="an OSM XML data file (typically a JOSM save file)",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="the name of the produced anki deck file (default=output.apkg)",
        default="output.apkg",
    )
    args = parser.parse_args()

    # Extract information from the OSM data file
    handler = MonumentHandler()
    handler.apply_file(args.osm_file)

    # Write the Anki note deck and log the card/note count
    deck = handler.flashcards
    genanki.Package(deck).write_to_file(args.output)
    card_count = len(deck.notes) * len(OSM_FEATURE_MODEL.templates)
    print(
        f"Wrote a deck of {card_count} cards (in {len(deck.notes)} notes)"
        f" to {args.output}"
    )
