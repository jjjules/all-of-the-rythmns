# Drum Pattern Generator

## Overview
This script generates all possible drum patterns for a given number of semiquavers (16th notes) and saves them as MusicXML files, which can be opened in notation software like MuseScore, Finale, or Sibelius.

### What it does:
- Creates every possible combination of hits and rests for a given number of beats.
- Organizes patterns by the number of notes, making it easier to explore rhythmic variations.
- Saves them in MusicXML format for easy editing and playback in notation software.
- Splits the patterns into multiple files if there are too many to fit in one.

## How to Use
### Requirements
- Python 3
- The `lxml` library (install it with `pip install lxml`)

### Running the Script
```sh
python script.py <N> [max_patterns_per_file]
```
- `<N>`: Number of semiquavers (16th notes) in each pattern (e.g., 8 for one bar in 4/4 time).
- `[max_patterns_per_file]` (optional): The maximum number of patterns per file. Defaults to 4096.

Example:
```sh
python script.py 8
```
This will generate all possible 8-note drum patterns and save them as MusicXML files.

## Features
- **Logical Organization**: Patterns are sorted so similar rhythms are grouped together.
- **Automatic File Splitting**: If too many patterns are generated, they are split into multiple files.
- **Customizable Output**: Optional features (like rehearsal marks and section breaks) can be enabled in the script.

## Opening the MusicXML Files
1. Open the `.musicxml` files in notation software like MuseScore, Finale, or Sibelius.
2. Play back and modify the patterns to create your own grooves.
3. Experiment with different subdivisions and note combinations to discover new rhythmic ideas!

## Why Use This?
This tool is great for:
- Drummers looking for fresh rhythmic ideas.
- Composers and arrangers wanting structured rhythm variations.
- Music educators teaching rhythm and pattern recognition.

Happy drumming!


