#!/usr/bin/env python3

import argparse
import functools
import genanki  # type: ignore
import geopandas as gp  # type: ignore
import html
import logging
import os
import prettymaps  # type: ignore

from anki_models import OSM_FEATURE_MODEL


def _get_osm_url(otype: str, oid: int) -> str:
    return f"https://www.openstreetmap.org/{otype}/{oid}"


# Anki needs unique deck ID, this one was generated randomly with
# random.randrange(1 << 30, 1 << 31)
# TODO: this should be a combined hash of the query and filtering information
MONUMENTS_DECK_ID = 1207021374


# The prettymaps preset used to render maps, cb-bf-f is mostly black-and-white, which
# makes it easy to highlight a single feature by changing its color.
TILE_PRESET = "cb-bf-f"


def _isolate_in_gdf(
    otype: str, oid: int, gdfs: dict[str, gp.GeoDataFrame]
) -> dict[str, gp.GeoDataFrame]:
    """Modify the given gdfs to contain only the OSM feature identified by (otype, oid)
    and return the gdfs"""
    buildings = gdfs["building"]
    isolated = buildings[buildings.index == (otype, oid)]
    gdfs["building"] = isolated
    return gdfs


def make_anki_package(query: str) -> genanki.Deck:
    """Fetch OSM data and create an anki package containing the notes and cards"""

    # List of media files to be included when finalizing the package
    media_files: list[str] = []

    # Query OSM and generate a tile for the whole area
    if not os.path.exists("tiles"):
        os.mkdir("tiles")
    global_nohl_plot = prettymaps.plot(
        query, preset=TILE_PRESET, figsize=(12, 12), save_as="tiles/global_nohl.jpg"
    )
    media_files.append("tiles/global_nohl.jpg")

    # Create a note for every monument that has a name
    buildings_gdf = global_nohl_plot.geodataframes["building"]
    monuments_gdf = buildings_gdf[buildings_gdf.heritage == "2"]

    deck = genanki.Deck(MONUMENTS_DECK_ID, "Monuments")
    for (otype, oid), monument in monuments_gdf.dropna(subset=["name"]).iterrows():
        # Generate a tile with this monument highlighted
        tile_name = f"global_hl_{oid}.jpg"
        isolate = functools.partial(_isolate_in_gdf, otype, oid)
        prettymaps.multiplot(
            prettymaps.Subplot(query),
            prettymaps.Subplot(
                query,
                postprocessing=isolate,
                style={"building": {"palette": ["#FF0000"]}},
            ),
            preset=TILE_PRESET,
            figsize=(12, 12),
            save_as=f"tiles/{tile_name}",
        )
        media_files.append(f"tiles/{tile_name}")

        # Create an anki note for this monument
        anki_note_fields = [
            monument["name"],
            '<img src="global_nohl.jpg">',
            f'<img src="{tile_name}">',
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
    logging.info(f"attaching filse: {media_files}")
    package.media_files = media_files
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
        help='an OSM search query, example: "Strasbourg, grande ile"',
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
