# OpenStreetMap Flashcards Generator

A [flashcard](https://en.wikipedia.org/wiki/Flashcard) generator based on
[OpenStreetMap](https://wiki.osmfoundation.org/wiki/Main_Page) data.

Will someday double as an [Anki](https://apps.ankiweb.net/) plugin, if I don't
get distracted before that.

## Usage

Invoke `osmfc.py` to generate an Anki deck file with proof-of-concept
flashcards:

```console
$ ./osmfc.py -v "Strasbourg grande ile"
[...an embarassing amount of warnings...]
INFO:root:Wrote a deck of 32 cards (in 16 notes) to output.apkg
```

In its current proof-of-concept state, the tool only builds anki cards for
the given area's buildings that are protected on a national level (OSM
features with `heritage=2` that are recognized as buildings by prettymaps). For
each of these, it create two cards: one asking the user to "place" the building
on a map of the area (mentaly, there is no interactivity other than anki's base
interface) and one showing the same map with the building highlighted and asking
what its name is.

## TODO

- try optimizing by using the SVG format and finding the correct elements in it
  to directly change their fill color without calling prettymaps.plot for each
  feature
    - if that works, maybe even find a way to do the highlighting (and zoom)
      with javascript, and thus using a single SVG image for the whole deck
    - otherwise rasterize the SVGs to JPG before inclusion in the deck to save
      space
- make the code more testable
- add example images to the README
- allow zooming on the feature with a single click
- build cards for some "obvious" object types like streets (warning: some are
  split into multiple ways);
- build PDF cards;
- make it a proper Python package;
- make it an anki plugin (while still supporting stand-alone use);
- build cards according to custom user queries;

Already used or potentially useful libraries:

- Anki deck generation: <https://github.com/kerrickstaley/genanki>
- OSM querying and tile rendering: <https://github.com/marceloprates/prettymaps>
