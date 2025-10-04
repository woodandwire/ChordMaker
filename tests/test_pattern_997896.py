#!/usr/bin/env python3
"""
Test the specific Pattern 997896 that should be impossible.
"""

from chord_validator import ChordFingeringValidator
from chord_chart import ChordChart

def test_pattern_997896():
    """Test the specific problematic pattern."""
    
    print("🔍 TESTING PATTERN 997896")
    print("=" * 40)
    
    # The exact pattern reported as impossible
    pattern = [('O', 0), ('X', 0), ('4', 5), ('3', 2), ('3', 2), ('4', 5)]
    
    print("Chord: Pattern 997896")
    print(f"Data: {pattern}")
    print()
    print("String Layout (6th to 1st):")
    string_names = ["6th (Low E)", "5th (A)", "4th (D)", "3rd (G)", "2nd (B)", "1st (High E)"]
    for i, (finger, fret) in enumerate(pattern):
        if finger == 'O':
            desc = f"O (Open)"
        elif finger == 'X':
            desc = f"X (Muted)"
        else:
            desc = f"{finger} (Fret {fret})"
        print(f"{string_names[i]}: {desc}")
    
    print()
    print("❌ WHY THIS SHOULD BE IMPOSSIBLE:")
    print("- Finger 3 (ring): Fret 2 on strings G & B")
    print("- Finger 4 (pinky): Fret 5 on strings D & High E") 
    print("- Ring finger at fret 2 blocks pinky from reaching fret 5")
    print("- 3-fret stretch between adjacent fingers is anatomically impossible")
    
    # Test with validator
    validator = ChordFingeringValidator()
    result = validator.validate_chord(pattern)
    
    print("\n" + "=" * 40)
    print("VALIDATOR RESULTS:")
    print(f"Is Valid: {result['is_valid']}")
    print(f"Status: {result.get('status_name', 'UNKNOWN')}")
    print()
    
    if result.get('messages'):
        print("Validation Messages:")
        for msg in result['messages']:
            print(f"  {msg['severity'].upper()}: {msg['message']}")
    else:
        print("No validation messages!")
    
    # Generate visualization
    chart = ChordChart()
    chart.set_chord_name("Pattern 997896 (Impossible?)")
    chart.save_to_file(pattern, "pattern_997896_test.svg")
    print(f"\n📊 Generated chart: pattern_997896_test.svg")
    
    return result

if __name__ == "__main__":
    result = test_pattern_997896()
    
    if result['is_valid']:
        print("\n🚨 PROBLEM CONFIRMED!")
        print("The validator incorrectly marked this impossible chord as VALID!")
        print("Need to enhance finger span validation for adjacent fingers.")
    else:
        print("\n✅ Validator correctly identified this as impossible.")