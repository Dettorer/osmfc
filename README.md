# OpenStreetMap Flashcards Generator

A [flashcard](https://en.wikipedia.org/wiki/Flashcard) generator based on
[OpenStreetMap](https://wiki.osmfoundation.org/wiki/Main_Page) data.

Will someday double as an [Anki](https://apps.ankiweb.net/) plugin, if I don't
get distracted before that.

## Usage

TODO when there is something concrete to use.

## TODO

- build anki cards;
- make it a proper Python package;
- make it an anki plugin (while still supporting stand-alone use);
- build OSM tiles and associate the names with their position on the tiles;
- build cards for some "obvious" object types like streets (warning: some are
  split into multiple ways);
- build cards according to custom user queries;
- automatically fetch OSM data to remove the need for a user-provided OSM XML
  file;
- ...

Already used or potentially useful libraries:

- XML analysis: <https://docs.osmcode.org/pyosmium/latest/intro.html>
- OSM APIs query: <https://github.com/mocnik-science/osm-python-tools/issues>
- Tile generation? <https://github.com/enzet/map-machine#tile-generation>
