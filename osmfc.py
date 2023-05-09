#!/usr/bin/env python3

import argparse
import functools
import osmium

from dataclasses import dataclass
from osmium.osm import types as otypes


@dataclass
class FlashCard:
    """The front and back of a flashcard"""

    front: str
    back: str

    osm_id: int
    osm_object_type: str


class MonumentHandler(osmium.SimpleHandler):
    """An osmium handler that creates flashcards about monument informations"""

    def __init__(self) -> None:
        super().__init__()
        self.flashcards: list[FlashCard] = []

    def _handle_object(self, o: otypes.OSMObject, object_type: str) -> None:
        name = o.tags.get("name")
        if o.tags.get("historic") == "monument" and name is not None:
            self.flashcards.append(FlashCard(name, str(o.id), o.id, object_type))

    node = functools.partialmethod(_handle_object, object_type="node")
    way = functools.partialmethod(_handle_object, object_type="way")
    relation = functools.partialmethod(_handle_object, object_type="relation")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="osmfc", description="A flashcard generator based on OpenStreetMap data"
    )
    parser.add_argument(
        "osm_file",
        help="an OSM XML data file (typically a JOSM save file)",
    )
    args = parser.parse_args()

    handler = MonumentHandler()
    handler.apply_file(args.osm_file)

    for card in handler.flashcards:
        print(
            f"https://www.openstreetmap.org/{card.osm_object_type}/{card.osm_id}:"
            f" {card.front} <-> {card.back}"
        )
