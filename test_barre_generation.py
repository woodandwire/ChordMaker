#!/usr/bin/env python3
"""
Test to verify that barre chord patterns (repeated fingers) are being generated.
"""

import itertools
from position_finder import PositionFinder, InstrumentConfig

def test_barre_generation():
    """Test that barre chord finger patterns are being generated."""
    
    print("Testing Barre Chord Pattern Generation")
    print("=" * 50)
    
    # Create a simple test with 3 fretted strings
    base_pattern = [('FRET', 1), ('FRET', 1), ('FRET', 2)]
    
    # Create position finder
    config = InstrumentConfig(strings=3, max_fret=3)  # Simple test case
    finder = PositionFinder(config)
    
    # Test the fixed finger assignment method
    patterns = finder.assign_fingers_to_pattern(base_pattern)
    
    print(f"Base pattern: {base_pattern}")
    print(f"Generated {len(patterns)} finger assignment patterns:")
    
    # Look for barre patterns (same finger repeated)
    barre_patterns = []
    unique_patterns = []
    
    for i, pattern in enumerate(patterns):
        fingers = [f for f, _ in pattern]
        
        # Check for repeated fingers (barre chords)
        if len(set(fingers)) < len(fingers):
            barre_patterns.append(pattern)
            print(f"  BARRE: {pattern} (fingers: {fingers})")
        else:
            unique_patterns.append(pattern)
            if i < 10:  # Show first 10 unique patterns
                print(f"  UNIQUE: {pattern} (fingers: {fingers})")
    
    print(f"\nSummary:")
    print(f"  Total patterns: {len(patterns)}")
    print(f"  Barre patterns: {len(barre_patterns)}")
    print(f"  Unique finger patterns: {len(unique_patterns)}")
    
    # Test specific barre cases
    print(f"\nExpected barre patterns found:")
    expected_barres = [
        ['1', '1', '2'],  # Index finger barre on first two strings
        ['1', '1', '1'],  # Index finger barre on all three strings
        ['2', '2', '3'],  # Middle finger barre
        ['3', '2', '2'],  # Ring finger on 1st, middle on others
    ]
    
    for expected in expected_barres:
        found = any(
            [f for f, _ in pattern] == expected 
            for pattern in patterns
        )
        status = "✅" if found else "❌"
        print(f"  {status} {expected}")
    
    return len(barre_patterns) > 0

def test_actual_generation():
    """Test actual pattern generation with a small limit to see barre chords."""
    
    print(f"\n" + "=" * 50)
    print("Testing Actual Pattern Generation (Limited)")
    print("=" * 50)
    
    # Create simple config for testing
    config = InstrumentConfig(strings=6, max_fret=3)
    finder = PositionFinder(config, output_dir="test_output")
    
    # Generate just a few patterns to see if barres show up
    patterns = finder.generate_string_patterns(limit=50)
    
    print(f"Generated {len(patterns)} total patterns")
    
    # Look for barre chord patterns
    barre_count = 0
    for i, pattern in enumerate(patterns):
        fingers = [f for f, fret in pattern if f not in ['O', 'X']]
        
        # Check for repeated fingers
        if fingers and len(set(fingers)) < len(fingers):
            barre_count += 1
            if barre_count <= 5:  # Show first 5 barre patterns
                print(f"  BARRE {barre_count}: {pattern}")
    
    print(f"\nFound {barre_count} barre chord patterns out of {len(patterns)} total patterns")
    return barre_count > 0

if __name__ == "__main__":
    # Test finger assignment
    barre_assignment_works = test_barre_generation()
    
    # Test actual generation
    barre_generation_works = test_actual_generation()
    
    print(f"\n" + "=" * 50)
    print("BARRE CHORD GENERATION TEST RESULTS")
    print("=" * 50)
    print(f"✅ Finger assignment supports barres: {barre_assignment_works}")
    print(f"✅ Pattern generation includes barres: {barre_generation_works}")
    
    if barre_assignment_works and barre_generation_works:
        print("🎸 SUCCESS: Barre chord patterns are now being generated!")
    else:
        print("❌ ISSUE: Barre chord generation still has problems")