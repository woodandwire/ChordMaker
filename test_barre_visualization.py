#!/usr/bin/env python3
"""
Test the enhanced barre chord visualization.
"""

from chord_chart import ChordChart

def test_barre_visualization():
    """Test barre chord visualization with known barre patterns."""
    
    chart = ChordChart()
    
    # Test Case 1: Pattern 99493 - finger 2 barre on strings 4&6 at fret 3
    print("=== Testing Pattern 99493 (Partial Barre) ===")
    pattern_99493 = [
        ('O', 0),  # String 1 (6th string) - open
        ('O', 0),  # String 2 (5th string) - open  
        ('1', 1),  # String 3 (4th string) - finger 1, fret 1
        ('2', 3),  # String 4 (3rd string) - finger 2, fret 3
        ('3', 5),  # String 5 (2nd string) - finger 3, fret 5
        ('2', 3)   # String 6 (1st string) - finger 2, fret 3 (BARRE with string 4)
    ]
    
    chart.set_chord_name("Pattern 99493 (Barre Test)")
    chart.save_to_file(pattern_99493, "test_barre_99493.svg")
    print("✓ Generated test_barre_99493.svg")
    print(f"Pattern data: {pattern_99493}")
    print("Should show barre line connecting strings 4&6 at fret 3\n")
    
    # Test Case 2: Full F Major barre chord
    print("=== Testing F Major (Full Barre) ===")
    f_major = [
        ('1', 1),  # String 1 - finger 1, fret 1 (barre)
        ('1', 1),  # String 2 - finger 1, fret 1 (barre)
        ('2', 2),  # String 3 - finger 2, fret 2
        ('3', 3),  # String 4 - finger 3, fret 3
        ('3', 3),  # String 5 - finger 3, fret 3 (partial barre)
        ('1', 1)   # String 6 - finger 1, fret 1 (barre)
    ]
    
    chart.set_chord_name("F Major (Full Barre)")
    chart.save_to_file(f_major, "test_barre_f_major.svg")
    print("✓ Generated test_barre_f_major.svg")
    print(f"Pattern data: {f_major}")
    print("Should show:")
    print("- Finger 1 barre across strings 1,2,6 at fret 1")
    print("- Finger 3 barre across strings 4,5 at fret 3\n")
    
    # Test Case 3: Pattern with no barres (control test)
    print("=== Testing Non-Barre Pattern (Control) ===")
    c_major = [
        ('X', 0),  # String 1 - muted
        ('3', 3),  # String 2 - finger 3, fret 3
        ('2', 2),  # String 3 - finger 2, fret 2
        ('O', 0),  # String 4 - open
        ('1', 1),  # String 5 - finger 1, fret 1
        ('O', 0)   # String 6 - open
    ]
    
    chart.set_chord_name("C Major (No Barre)")
    chart.save_to_file(c_major, "test_no_barre_c_major.svg")
    print("✓ Generated test_no_barre_c_major.svg")
    print(f"Pattern data: {c_major}")
    print("Should show individual finger positions with no connecting lines\n")
    
    print("=== Barre Visualization Test Complete ===")
    print("Open the generated SVG files to verify barre line visualization!")

if __name__ == "__main__":
    test_barre_visualization()