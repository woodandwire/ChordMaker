"""
Utility functions for chord file operations and data extraction.
"""
import os
import glob
import re
from pathlib import Path


def extract_chord_data_from_svg(svg_file_path):
    """Extract chord data from SVG file comment."""
    try:
        with open(svg_file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for CHORD_DATA comment
        match = re.search(r'<!-- CHORD_DATA: (.+?) -->', content)
        if match:
            chord_data_str = match.group(1)
            # Parse the chord data string back to a list
            # This will handle the string representation of the list
            chord_data = eval(chord_data_str)  # Safe here since we control the input
            return chord_data
        
        return None
    except Exception:
        return None


def format_chord_data_for_copy(chord_data, chord_name):
    """Format chord data in a copy-friendly format for debugging."""
    if not chord_data:
        return "No chord data available"
    
    # Create a formatted string that's easy to copy and paste
    formatted = f"""Chord: {chord_name}
Data: {chord_data}

String Layout (6th to 1st):
"""
    
    string_names = ["6th (Low E)", "5th (A)", "4th (D)", "3rd (G)", "2nd (B)", "1st (High E)"]
    for i, (string_type, fret) in enumerate(chord_data):
        if string_type == 'X':
            fret_desc = "Muted"
        elif string_type == 'O':
            fret_desc = "Open"
        else:
            fret_desc = f"Fret {fret}"
        
        formatted += f"{string_names[i]}: {string_type} ({fret_desc})\n"
    
    return formatted


def discover_chord_files(base_dir):
    """Discover all chord SVG files in the chords directory."""
    chord_files = []
    
    # Look for files matching the pattern *_chord.svg in the chords directory
    pattern = str(base_dir / "chords" / "*_chord.svg")
    svg_files = glob.glob(pattern)
    
    for svg_file in svg_files:
        file_path = Path(svg_file)
        # Extract chord name from filename (remove _chord.svg suffix)
        chord_name = file_path.stem.replace("_chord", "")
        
        # Convert filename back to display name
        display_name = chord_name.replace("_", " ").replace("sharp", "#").replace("flat", "b")
        display_name = display_name.title()  # Capitalize words
        
        chord_files.append({
            "filename": chord_name,
            "display_name": display_name,
            "file_path": file_path
        })
    
    # Sort by display name
    chord_files.sort(key=lambda x: x["display_name"])
    return chord_files


def sanitize_chord_name(chord_name):
    """Sanitize chord name for use as filename."""
    # Replace problematic characters for file naming
    safe_name = chord_name.replace("#", "sharp").replace("b", "flat")
    safe_name = re.sub(r'[^\w\s-]', '', safe_name)  # Remove special characters
    safe_name = re.sub(r'[-\s]+', '_', safe_name)  # Replace spaces and hyphens with underscores
    return safe_name.lower()