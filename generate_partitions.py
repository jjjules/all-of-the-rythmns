import sys
from lxml import etree
from itertools import product
import math

def generate_binary_patterns(n: int) -> list[list[int]]:
    """Generate all possible binary patterns of length n (1 = note, 0 = rest)."""
    return [list(p) for p in product([0, 1], repeat=n)]

def sort_patterns(patterns: list[list[int]], n: int) -> list[list[int]]:
    """Sort patterns based on the total number of notes and lexicographical order."""
    for pat in patterns:
        pat.extend([sum(pat)] + [-x for x in pat])
    patterns = sorted(patterns, key=lambda x: x[n:])
    return [x[:n] for x in patterns]

def split_patterns(patterns: list[list[int]], max_patterns_per_file: int) -> list[list[list[int]]]:
    """Split patterns into chunks while preserving logical structure."""
    assert math.log(max_patterns_per_file, 2).is_integer()
    num_files = len(patterns) // max_patterns_per_file
    num_bits_for_splits = int(math.log2(num_files))
    
    split_groups = [[] for _ in range(num_files)]
    for pattern in patterns:
        index = 0  # Distribute patterns logically based on first notes
        for i, x in enumerate(pattern[-num_bits_for_splits:]):
            index += x << i
        split_groups[index].append(pattern)
    
    return split_groups

def generate_drum_partitions(
    n: int,
    max_patterns_per_file: int = 4096,
    use_rehearsal_marks=False,
    use_section_breaks=False,
    use_text_annotations=False
):
    """Generate MusicXML files containing all possible partitions for N semiquavers,
    with each pattern in a separate measure. Automatically splits output files if needed.
    
    Parameters:
    n (int): Number of semiquavers in each pattern.
    max_patterns_per_file (int): Maximum number of patterns per output file.
    use_rehearsal_marks (bool): If True, add chapter markers when note count changes.
    use_section_breaks (bool): If True, insert section breaks when note count changes.
    use_text_annotations (bool): If True, add text annotations for sections.
    
    Output:
    Generates MusicXML files named "drum_partitions_N{n}_part{X}.musicxml".
    """
    
    if not math.log(n, 2).is_integer():
        temp = max_patterns_per_file
        max_patterns_per_file = 2 ** int(math.log2(n))
        print(f"Warning: Using {max_patterns_per_file} instead of {temp} as the maximum number of pattern per file should be a power of 2.")

    # Generate and sort all possible binary patterns
    patterns = generate_binary_patterns(n)
    patterns = sort_patterns(patterns, n)
    
    # Split patterns into structured groups
    patterns_split = split_patterns(patterns, max_patterns_per_file)
    
    for file_idx, patterns_subset in enumerate(patterns_split):
        # Create root XML element for the MusicXML file
        root = etree.Element("score-partwise", version="3.1")
        part_list = etree.SubElement(root, "part-list")
        score_part = etree.SubElement(part_list, "score-part", id="P1")
        etree.SubElement(score_part, "part-name").text = "Drums"
        part = etree.SubElement(root, "part", id="P1")

        previous_note_count = None
        
        for idx, pattern in enumerate(patterns_subset, start=1):
            note_count = sum(pattern)  # Count number of played notes
            measure = etree.SubElement(part, "measure", number=str(idx))
            attributes = etree.SubElement(measure, "attributes")
            etree.SubElement(attributes, "divisions").text = "4"  # Defines semiquaver resolution
            
            if idx == 1:
                # Define time signature (N/16)
                time = etree.SubElement(attributes, "time")
                etree.SubElement(time, "beats").text = str(n)
                etree.SubElement(time, "beat-type").text = "16"
            
            # Define percussion clef
            clef = etree.SubElement(attributes, "clef")
            etree.SubElement(clef, "sign").text = "percussion"
            etree.SubElement(clef, "line").text = "2"
            
            # Insert markers if note count changes
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
            
            # Convert binary pattern into notes and rests in MusicXML
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

        # Define filename and save MusicXML file
        if len(patterns_split) > 1:
            filename = f"output/drum_partitions_N{n}_part{file_idx+1}.musicxml"
        else:
            filename = f"output/drum_partitions_N{n}.musicxml"
        tree = etree.ElementTree(root)
        with open(filename, "wb") as f:
            tree.write(f, pretty_print=True, xml_declaration=True, encoding="UTF-8")
        
        print(f"Generated: {filename}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <N> [max_patterns_per_file]")
        sys.exit(1)
    
    # Read command-line arguments
    N = int(sys.argv[1])
    max_patterns_per_file = int(sys.argv[2]) if len(sys.argv) > 2 else 4096
    
    # Generate partitions with default feature flags set to False
    generate_drum_partitions(N, max_patterns_per_file, use_rehearsal_marks=False, use_section_breaks=False, use_text_annotations=False)

