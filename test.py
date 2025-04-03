#!/bin/python

from lxml import etree

def create_musicxml():
    root = etree.Element("score-partwise", version="3.1")

    # Define part list
    part_list = etree.SubElement(root, "part-list")
    score_part = etree.SubElement(part_list, "score-part", id="P1")
    etree.SubElement(score_part, "part-name").text = "Drums"

    # Define the part (Drum Notation)
    part = etree.SubElement(root, "part", id="P1")

    # Define measure
    measure = etree.SubElement(part, "measure", number="1")

    # Define attributes (time signature, clef, percussion)
    attributes = etree.SubElement(measure, "attributes")
    etree.SubElement(attributes, "divisions").text = "1"

    # Time signature 4/4
    time = etree.SubElement(attributes, "time")
    etree.SubElement(time, "beats").text = "4"
    etree.SubElement(time, "beat-type").text = "4"

    # Percussion clef
    clef = etree.SubElement(attributes, "clef")
    etree.SubElement(clef, "sign").text = "percussion"
    etree.SubElement(clef, "line").text = "2"

    # Add four quarter notes (snare drum on line 2)
    for _ in range(4):
        note = etree.SubElement(measure, "note")
        pitch = etree.SubElement(note, "unpitched")
        etree.SubElement(pitch, "display-step").text = "C"
        etree.SubElement(pitch, "display-octave").text = "4"
        duration = etree.SubElement(note, "duration")
        duration.text = "1"
        type_tag = etree.SubElement(note, "type")
        type_tag.text = "quarter"
        percussion = etree.SubElement(note, "instrument", id="drumset")

    # Save to file
    tree = etree.ElementTree(root)
    with open("drum_partition.musicxml", "wb") as f:
        tree.write(f, pretty_print=True, xml_declaration=True, encoding="UTF-8")

    print("MusicXML file generated: drum_partition.musicxml")

create_musicxml()

