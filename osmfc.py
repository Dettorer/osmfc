#!/usr/bin/env python3

import argparse
import genanki
import html
import logging
import os
import prettymaps

from anki_models import OSM_FEATURE_MODEL


def _get_osm_url(otype: str, oid: int) -> str:
    return f"https://www.openstreetmap.org/{otype}/{oid}"


# Anki needs unique deck ID, this one was generated randomly with
# random.randrange(1 << 30, 1 << 31)
# TODO: this should be a combined hash of the query and filtering information
MONUMENTS_DECK_ID = 1725870212


def make_anki_package(query: str) -> genanki.Deck:
    """Fetch OSM data and create an anki package containing the notes and cards"""

    # Query OSM and generate a tile for the whole area
    plot = prettymaps.plot(query)
    if not os.path.exists("tiles"):
        os.mkdir("tiles")
    plot.fig.savefig("tiles/global.jpg")

    # Create a note for every monument that has a name
    buildings_gdf = plot.geodataframes["building"]
    monuments_gdf = buildings_gdf[buildings_gdf.heritage == "2"]

    deck = genanki.Deck(MONUMENTS_DECK_ID, "Monuments")
    for (otype, oid), monument in monuments_gdf.dropna(subset=["name"]).iterrows():
        # Create an anki note for this monument
        anki_note_fields = [
            monument["name"],
            '<img src="global.jpg">',
            html.escape(_get_osm_url(otype, oid)),
        ]
        deck.add_note(
            genanki.Note(
                model=OSM_FEATURE_MODEL,
                fields=anki_note_fields,
            )
        )

        logging.info(f"Created a note for OSM feature {oid}")
        logging.debug(f"The note for feature {oid} has fields {anki_note_fields}")

    # Output the anki package and log the cards and notes count
    package = genanki.Package(deck)
    package.media_files = ["tiles/global.jpg"]
    package.write_to_file(args.output)
    card_count = len(deck.notes) * len(OSM_FEATURE_MODEL.templates)
    logging.info(
        f"Wrote a deck of {card_count} cards (in {len(deck.notes)} notes)"
        f" to {args.output}"
    )

    return deck


if __name__ == "__main__":
    # Handle command line arguments
    parser = argparse.ArgumentParser(
        prog="osmfc", description="A flashcard generator based on OpenStreetMap data"
    )
    parser.add_argument(
        "query",
        help="an OSM XML data file (typically a JOSM save file)",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="the name of the produced anki deck file (default=output.apkg)",
        default="output.apkg",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="increase the logging level, repeat the option to increase further",
        action="count",
        default=0,
    )
    args = parser.parse_args()

    # Set the logging level
    verbosity_to_log_level = {
        0: logging.WARNING,
        1: logging.INFO,
        2: logging.DEBUG,
    }
    logging.basicConfig(level=verbosity_to_log_level[args.verbose])

    make_anki_package(args.query)
