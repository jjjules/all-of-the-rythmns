import sys
import os
from lxml import etree
from itertools import product
import math

MAX_PATTERNS_PER_FILE = 4096

def generate_binary_patterns(n: int) -> list[list[int]]:
    """Generate all possible binary patterns of length n (1 = note, 0 = rest)."""
    return [list(p) for p in product([0, 1], repeat=n)]

def sort_patterns(patterns: list[list[int]], n: int) -> list[list[int]]:
    """Sort patterns based on the total number of notes and lexicographical order."""
    for pat in patterns:
        pat.extend([sum(pat)] + [-x for x in pat])
    patterns = sorted(patterns, key=lambda x: x[n:])
    return [x[:n] for x in patterns]

def split_patterns_wrt_last_bits(patterns: list[list[int]], max_patterns_per_file: int) -> list[list[list[int]]]:
    """Split patterns into chunks while preserving logical structure with respect to last bits of patterns."""
    assert math.log(max_patterns_per_file, 2).is_integer()
    num_files = math.ceil(len(patterns) / max_patterns_per_file)

    if num_files == 1:
        return [patterns]
    
    split_groups = [[] for _ in range(num_files)]
    num_bits_for_splits = int(math.log2(num_files))
    for pattern in patterns:
        index = 0  # Distribute patterns logically based on first notes
        for i, x in enumerate(pattern[-num_bits_for_splits:]):
            index += x << i
        split_groups[index].append(pattern)
    
    return split_groups

def generate_drum_partitions(
    n: int,
    max_patterns_per_file: int = 4096,
):
    """Generate MusicXML files containing all possible partitions for N semiquavers,
    with each pattern in a separate measure. Automatically splits output files if needed.
    
    Parameters:
    n (int): Number of semiquavers in each pattern.
    max_patterns_per_file (int): Maximum number of patterns per output file.
    
    Output:
    Generates MusicXML files named "drum_partitions_N{n}_part{X}.musicxml".
    """
    
    num_patterns = 2 ** n
    if max_patterns_per_file > num_patterns:
        max_patterns_per_file = num_patterns
    elif not math.log(n, 2).is_integer():
        temp = max_patterns_per_file
        max_patterns_per_file = 2 ** int(math.log2(max_patterns_per_file))
        print(f"Warning: Using {max_patterns_per_file} instead of {temp} as the maximum number of pattern per file should be a power of 2.")

    # Generate and sort all possible binary patterns
    patterns = generate_binary_patterns(n)
    patterns = sort_patterns(patterns, n)
    
    # Split patterns into structured groups
    splitting = 'normal'
    match splitting:
        case 'normal':
            num_files = int(len(patterns) / max_patterns_per_file)
            num_patterns_per_file = int(num_patterns / num_files)
            patterns_split = [patterns[i * num_patterns_per_file: (i+1) * num_patterns_per_file] for i in range(num_files)]
        case 'by_end_bits':
            patterns_split = split_patterns_wrt_last_bits(patterns, max_patterns_per_file)
        case _:
            raise ValueError("The splitting must be 'normal' or 'by_end_bits'.")
    
    for file_idx, patterns_subset in enumerate(patterns_split):
        # Create root XML element for the MusicXML file
        root = etree.Element("score-partwise", version="3.1")
        part_list = etree.SubElement(root, "part-list")
        score_part = etree.SubElement(part_list, "score-part", id="P1")
        etree.SubElement(score_part, "part-name").text = "Claves"
        part = etree.SubElement(root, "part", id="P1")
        
        for idx, pattern in enumerate(patterns_subset, start=1):
            measure = etree.SubElement(part, "measure", number=str(idx))
            attributes = etree.SubElement(measure, "attributes")
            etree.SubElement(attributes, "divisions").text = "4"  # Defines semiquaver resolution
            etree.SubElement(attributes, "divisions").text = "4"  # Defines semiquaver resolution
            
            if idx == 1:
                # Define time signature
                time = etree.SubElement(attributes, "time")
                if n % 4 == 0:
                    etree.SubElement(time, "beats").text = str(int(n / 4))
                    etree.SubElement(time, "beat-type").text = "4"
                else:
                    etree.SubElement(time, "beats").text = str(n)
                    etree.SubElement(time, "beat-type").text = "16"
            
            # Define percussion clef
            clef = etree.SubElement(attributes, "clef")
            etree.SubElement(clef, "sign").text = "percussion"
            etree.SubElement(clef, "line").text = "2"

            # Set staff to a single rhythm line
            staff_details = etree.SubElement(attributes, "staff-details")
            etree.SubElement(staff_details, "staff-lines").text = "1"

            
            # Convert binary pattern into notes and rests in MusicXML
            for bit in pattern:
                note = etree.SubElement(measure, "note")
                stem_tag = etree.SubElement(note, "stem")
                stem_tag.text = "up"
                duration = etree.SubElement(note, "duration")
                duration.text = "1"  # Semiquaver duration
                type_tag = etree.SubElement(note, "type")
                type_tag.text = "16th"
                
                if bit == 1:
                    pitch = etree.SubElement(note, "unpitched")
                    etree.SubElement(pitch, "display-step").text = "F"
                    etree.SubElement(pitch, "display-octave").text = "5"
                    etree.SubElement(note, "instrument", id="claves")
                else:
                    etree.SubElement(note, "rest")

        # Define filename and save MusicXML file
        if not os.path.exists("output"):
            os.makedirs("output")
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
    max_patterns_per_file = int(sys.argv[2]) if len(sys.argv) > 2 else MAX_PATTERNS_PER_FILE
    
    # Generate partitions with default feature flags set to False
    generate_drum_partitions(N, max_patterns_per_file)

