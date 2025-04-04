import sys
from lxml import etree
from itertools import product

def generate_binary_patterns(n: int) -> list[list[int]]:
    """Generate all possible binary patterns of length n (1 = note, 0 = rest)."""
    return list(map(lambda x: list(x), list(product([0, 1], repeat=n))))

def generate_drum_partitions(n: int, use_rehearsal_marks=False, use_section_breaks=False, use_text_annotations=False):
    """Generate a single MusicXML file containing all possible partitions for N semiquavers,
    with each pattern in a separate measure.
    
    Parameters:
    n (int): Number of semiquavers in each pattern.
    use_rehearsal_marks (bool): If True, add chapter markers when note count changes.
    use_section_breaks (bool): If True, insert section breaks when note count changes.
    use_text_annotations (bool): If True, add text annotations for sections.
    
    Output:
    Generates a MusicXML file named "drum_partitions_N{n}.musicxml".
    """
    
    root = etree.Element("score-partwise", version="3.1")

    # Generate all patterns and sort them intuitively
    patterns = generate_binary_patterns(n)
    sort_list = []
    for pat in patterns:
        pat.extend([sum(pat)] + [- x for x in pat])
    patterns = sorted(patterns, key = lambda x: x[n:])
    patterns = [x[:n] for x in patterns]
    
    # Define part list
    part_list = etree.SubElement(root, "part-list")
    score_part = etree.SubElement(part_list, "score-part", id="P1")
    etree.SubElement(score_part, "part-name").text = "Drums"
    
    # Define the part (Drum Notation)
    part = etree.SubElement(root, "part", id="P1")
    
    previous_note_count = None
    
    for idx, pattern in enumerate(patterns):
        note_count = sum(pattern)  # Number of notes in this pattern
        
        measure = etree.SubElement(part, "measure", number=str(idx+1))
        attributes = etree.SubElement(measure, "attributes")
        etree.SubElement(attributes, "divisions").text = "4"  # Semiquaver resolution
        
        if idx == 0:
            time = etree.SubElement(attributes, "time")
            etree.SubElement(time, "beats").text = f"{n}"
            etree.SubElement(time, "beat-type").text = "16"
        
        clef = etree.SubElement(attributes, "clef")
        etree.SubElement(clef, "sign").text = "percussion"
        etree.SubElement(clef, "line").text = "2"
        
        # Insert chapter separation if note count changes
        if previous_note_count is not None and note_count != previous_note_count:
            if use_rehearsal_marks:
                rehearsal_mark = etree.SubElement(measure, "direction")
                direction_type = etree.SubElement(rehearsal_mark, "direction-type")
                etree.SubElement(direction_type, "rehearsal").text = f"Chapter: {note_count} Notes"
            
            if use_section_breaks:
                section_break = etree.SubElement(measure, "barline", location="right")
                etree.SubElement(section_break, "bar-style").text = "light-heavy"
                etree.SubElement(section_break, "repeat", direction="forward")
            
            if use_text_annotations:
                text_annotation = etree.SubElement(measure, "direction")
                direction_type = etree.SubElement(text_annotation, "direction-type")
                words = etree.SubElement(direction_type, "words")
                words.text = f"Section: {note_count} Notes"
        
        previous_note_count = note_count
        
        # Convert binary pattern to MusicXML
        for bit in pattern:
            note = etree.SubElement(measure, "note")
            duration = etree.SubElement(note, "duration")
            duration.text = "1"  # Semiquaver duration
            type_tag = etree.SubElement(note, "type")
            type_tag.text = "16th"
            
            if bit == 1:
                pitch = etree.SubElement(note, "unpitched")
                etree.SubElement(pitch, "display-step").text = "C"
                etree.SubElement(pitch, "display-octave").text = "4"
                etree.SubElement(note, "instrument", id="drumset")
            else:
                etree.SubElement(note, "rest")
    
    # Save to file
    filename = f"output/drum_partitions_N{n}.musicxml"
    tree = etree.ElementTree(root)
    with open(filename, "wb") as f:
        tree.write(f, pretty_print=True, xml_declaration=True, encoding="UTF-8")
    
    print(f"Generated: {filename}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <N>")
        sys.exit(1)
    
    N = int(sys.argv[1])
    generate_drum_partitions(N, use_rehearsal_marks=False, use_section_breaks=False, use_text_annotations=False)
