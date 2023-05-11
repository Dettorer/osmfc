# OpenStreetMap Flashcards Generator

A [flashcard](https://en.wikipedia.org/wiki/Flashcard) generator based on
[OpenStreetMap](https://wiki.osmfoundation.org/wiki/Main_Page) data.

Will someday double as an [Anki](https://apps.ankiweb.net/) plugin, if I don't
get distracted before that.

## Usage

Invoke `osmfc.py` to generate an Anki deck file with proof-of-concept flashcards
based on a given OSM XML data file:

```console
$ ./osmfc.py example_osm_data_files/Strasourg_city_center.osm
Wrote a deck of 10 cards (in 5 notes) to output.apkg
```

In its current state, the tool only builds cards associating the name and the
OSM ID of the monuments (OSM features with tag `historic=monument` or
`heritage=2`) contained in the given data file. The output file can then be
imported in Anki as a new deck.

## TODO

- render OSM tiles and associate the names with their position on the tiles;
- build PDF cards;
- make it a proper Python package;
- make it an anki plugin (while still supporting stand-alone use);
- build cards for some "obvious" object types like streets (warning: some are
  split into multiple ways);
- build cards according to custom user queries;
- automatically fetch OSM data to remove the need for a user-provided OSM XML
  file;
- ...

Already used or potentially useful libraries:

- XML analysis: <https://docs.osmcode.org/pyosmium/latest/intro.html>
- Anki deck generation: <https://github.com/kerrickstaley/genanki>
- OSM APIs query: <https://github.com/mocnik-science/osm-python-tools/issues>
- Tile generation? <https://github.com/enzet/map-machine#tile-generation>
