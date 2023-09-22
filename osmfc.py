#!/usr/bin/env python3

import argparse
import datetime
import genanki  # type: ignore
import geopandas as gp  # type: ignore
import hashlib
import html
import logging
import os
import prettymaps  # type: ignore
from lxml import etree  # type: ignore
from typing import Callable

from anki_models import make_anki_model


def _get_osm_url(otype: str, oid: int) -> str:
    return f"https://www.openstreetmap.org/{otype}/{oid}"


# The prettymaps preset used to render maps, cb-bf-f is mostly black-and-white, which
# makes it easy to highlight a single feature by changing its color.
TILE_PRESET = "cb-bf-f"


def fetch_gdfs(query: str) -> tuple[gp.GeoDataFrame, gp.GeoDataFrame]:
    """Fetch OSM data for the given query

    Returns two geodataframes:
        - the first is the perimeter of the query
        - the second is the osm features in the query
    """
    # Get our preset's data
    layers, _, _, radius, dilate = prettymaps.draw.manage_presets(
        load_preset=TILE_PRESET,
        save_preset=False,
        update_preset=None,
        # TODO: add the query's extra tags to make sure we fetch every feature we need
        layers={},
        style={},
        circle=None,
        radius=None,
        dilate=None,
    )

    # Fetch and merge the geodataframes
    gdfs = prettymaps.fetch.get_gdfs(query, layers, radius, dilate)  # type: ignore
    perimeter = gdfs["perimeter"]
    features = gp.pd.concat([gdfs[layer] for layer in layers])

    # XXX: ignore because mypy thinks pd.DataFrame is incompatible with gp.GeoDataFrame
    return perimeter, features  # type: ignore


def get_osmids_matching_tags(
    gdf: gp.GeoDataFrame, tags: dict[str, str]
) -> list[tuple[str, int]]:
    """Return the OSM IDs of the features in the given GeoDataFrame that match the given
    tags"""
    for tag, value in tags.items():
        gdf = gdf[gdf[tag] == value].dropna(subset=["name"])  # type: ignore
    logging.info(f"Found {len(gdf)} features matching the given tags")
    return gdf.index.tolist()


def normalize_osmid(osmid: tuple[str, int]) -> str:
    """Normalize an OSM ID to the format used by OSMnx

    Example: ('way', 1234) -> 'W1234'
    """
    otype, oid = osmid
    return f"{otype[0].upper()}{oid}"


def build_anotated_svg_map(
    perimeter: gp.GeoDataFrame, osmids: list[tuple[str, int]], session_hash: str
) -> str:
    """Build an SVG map of the given perimeter with the given features annotated by
    their osmid

    Returns: the string representation of an SVG image"""
    # normalize the osmids
    normalized_osmids = list(map(normalize_osmid, osmids))

    # We define one layer per feature, identified by its osmid. This allows us to define
    # a different style for each feature.
    layers = {oid: {"osmid": oid} for oid in normalized_osmids}

    # We then define a style for each of these features that hacks the "url" property to
    # be the osmid. This "url" property ends up in the SVG, so we can use it to
    # postprocess the image to highlight any feature we want. Most notably, this
    # postprocessing can be done by any program that uses the SVG, such as anki.
    # We style the features with a red fill color, but make them transparent later in
    # this function. This way, they only need to be made visible again to highlight the
    # feature.
    style = {
        oid: {"url": oid, "zorder": 10, "fc": "#ff0000"} for oid in normalized_osmids
    }

    # Render the map
    if not os.path.exists("media"):
        os.mkdir("media")
    file_path = os.path.join("media", session_hash + ".svg")
    prettymaps.plot(
        perimeter,
        preset=TILE_PRESET,
        layers=layers,
        style=style,
        figsize=(12, 12),
        save_as=file_path,
    )

    # Postprocess the SVG: use the "url" property we injected earlier to add the osmid
    # as an "id" attribute for each feature's path tag and make them transparent. This
    # allows the card renderer (e.g. anki) to quickly find any feature's svg path later
    # and highlight it.
    svg_tree = etree.parse(file_path)
    svg_element = svg_tree.getroot()
    for url_tag in svg_element.findall(".//{http://www.w3.org/2000/svg}a"):
        osmid = url_tag.attrib.get("{http://www.w3.org/1999/xlink}href")
        if osmid is None:
            # This element does not belong to a feature we identified, skip it
            continue

        feature_path = url_tag.find("{http://www.w3.org/2000/svg}path")
        feature_path.attrib["id"] = osmid
        feature_path.attrib["style"] += "; opacity: 0"

    # TODO: try to rasterize the preset's layers to save space and only keep the
    # features' extra shapes as SVG to allow the anki cards to highlight them

    return etree.tostring(svg_tree, encoding="unicode")


def make_anki_package(query: str, tags: dict[str, str]) -> genanki.Deck:
    """Fetch OSM data and create an anki package containing the notes and cards"""

    # Get a hash of the current query and tags to use as a anki deck ID. Not including
    # the date in this ID ensures that if a user re-runs the same query later, they can
    # use the new deck to update an existing one, instead of duplicating it.
    query_hash = hashlib.sha256(query.encode("utf-8"))  # query
    query_hash.update(str(tags).encode("utf-8"))  # tags
    # Get a hash of the current session, which includes the query, the tags and the
    # current date.
    session_hash = query_hash.copy()
    session_hash.update(datetime.datetime.now().isoformat().encode("utf-8"))  # date

    # List of media files to be included when finalizing the package
    media_files: list[str] = []

    # Query OSM and generate a map of the whole area, with the features we want to make
    # cards with annotated by their osmid in the SVG document itself. Use the session
    # hash as the name of the SVG file.
    perimeter, features = fetch_gdfs(query)
    osmids = get_osmids_matching_tags(features, tags)
    map_image = build_anotated_svg_map(perimeter, osmids, session_hash.hexdigest())

    # Initialize the anki deck, using the session hash as the deck ID, but clamped to 64
    # bits (including sign bit) to allow genanki to store it in an sqlite database
    deck_id = int(session_hash.hexdigest(), 16) % (2**63)
    deck = genanki.Deck(deck_id, "Monuments")
    note_model = make_anki_model(deck_id, map_image)

    # Create a note for every monument that has a name
    monuments_gdf = features[features.index.isin(osmids)]
    for (otype, oid), monument in monuments_gdf.dropna(subset=["name"]).iterrows():
        osmid = normalize_osmid((otype, oid))

        # Create an anki note for this monument
        anki_note_fields = [
            monument["name"],
            osmid,
            html.escape(_get_osm_url(otype, oid)),
        ]
        deck.add_note(
            genanki.Note(
                model=note_model,
                fields=anki_note_fields,
            )
        )

        logging.info(f'Created a note for OSM feature {osmid}: "{monument["name"]}""')
        logging.debug(f"The note for feature {osmid} has fields {anki_note_fields}")

    # Output the anki package and log the cards and notes count
    package = genanki.Package(deck)
    logging.info(f"attaching files: {media_files}")
    package.media_files = media_files
    package.write_to_file(args.output)
    card_count = len(deck.notes) * len(note_model.templates)
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

    make_anki_package(args.query, {"heritage": "2"})
