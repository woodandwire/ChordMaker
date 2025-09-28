#!/usr/bin/env python3
"""
Test script to verify the VD abbreviation fix for Very Difficult chords.
"""

from chord_chart import ChordChart

def test_vd_abbreviation():
    """Test that Very Difficult chords use VD abbreviation."""
    
    # Test a very difficult chord
    chord_data = [('X', 0), ('X', 0), ('1', 2), ('2', 3), ('3', 5), ('4', 6)]
    
    chart = ChordChart()
    chart.set_chord_name("Test VD")
    
    svg_content = chart.create_grid_chart(chord_data)
    chart.save_to_file(chord_data, "chords/test_vd_fix.svg")
    
    print("Generated test chord with VD abbreviation...")
    print("Check chords/test_vd_fix.svg for the complexity score display.")
    
    # Look for VD in the SVG content
    if "VD" in svg_content:
        print("✓ Found VD abbreviation in SVG content")
    else:
        print("✗ VD abbreviation not found - checking what's there...")
        # Find the complexity score line
        lines = svg_content.split('\n')
        for line in lines:
            if 'text-anchor="end"' in line:
                print(f"Found complexity line: {line.strip()}")

if __name__ == "__main__":
    test_vd_abbreviation()