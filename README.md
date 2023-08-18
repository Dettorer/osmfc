# OpenStreetMap Flashcards Generator

A [flashcard](https://en.wikipedia.org/wiki/Flashcard) generator based on
[OpenStreetMap](https://wiki.osmfoundation.org/wiki/Main_Page) data.

Will someday double as an [Anki](https://apps.ankiweb.net/) plugin, if I don't
get distracted before that.

## Usage

Invoke `osmfc.py` to generate an Anki deck file with proof-of-concept
flashcards:

```console
$ ./osmfc.py "Strasbourg grande ile"
Wrote a deck of 10 cards (in 5 notes) to output.apkg
```

In its current state, the tool only builds cards associating the name of the
area's monuments (OSM features with tag `historic=monument` or `heritage=2`) and
a single rendered tile of the entire area. The output file can then be imported
in Anki as a new deck.

## TODO

- generate one more image per note where the relevant OSM object is highlighted
- build cards for some "obvious" object types like streets (warning: some are
  split into multiple ways);
- build PDF cards;
- make it a proper Python package;
- make it an anki plugin (while still supporting stand-alone use);
- build cards according to custom user queries;

Already used or potentially useful libraries:

- Anki deck generation: <https://github.com/kerrickstaley/genanki>
- OSM querying and tile rendering: <https://github.com/marceloprates/prettymaps>
